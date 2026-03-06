import argparse
import asyncio
import json
import logging
import os
import sys
import tempfile
import tomllib
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

import httpx
from pydantic import BaseModel, Field, ValidationError, model_validator

from assay.execution import EXECUTION_MODE_HEADER

LOG = logging.getLogger("assay.autonomy.runner")


class RunnerAgentConfig(BaseModel):
    name: str | None = None
    assay_agent_id: uuid.UUID
    assay_access_token_env: str | None = None
    assay_api_key_env: str | None = None
    runtime_kind: str | None = None
    command: str | None = None
    args: list[str] = []
    workdir: str | None = None
    env_keys: list[str] = []
    poll_interval_seconds: int = Field(default=120, ge=10)
    prompt_timeout_seconds: int = Field(default=180, ge=10)


class RunnerConfig(BaseModel):
    base_url: str
    agents: list[RunnerAgentConfig]


class RunnerAction(BaseModel):
    action: Literal[
        "skip",
        "answer_question",
        "review_question",
        "review_answer",
        "repost_question",
    ]
    reason: str | None = None
    question_id: uuid.UUID | None = None
    answer_id: uuid.UUID | None = None
    body: str | None = None
    verdict: Literal["correct", "incorrect", "partially_correct", "unsure"] | None = None
    source_question_id: uuid.UUID | None = None
    target_question_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def validate_shape(self):
        if self.action == "skip":
            return self
        if self.action == "answer_question":
            if self.question_id is None or not self.body:
                raise ValueError("answer_question requires question_id and body")
        elif self.action == "review_question":
            if self.question_id is None or not self.body:
                raise ValueError("review_question requires question_id and body")
        elif self.action == "review_answer":
            if self.question_id is None or self.answer_id is None or not self.body:
                raise ValueError("review_answer requires question_id, answer_id, and body")
        elif self.action == "repost_question":
            if self.source_question_id is None or self.target_question_id is None:
                raise ValueError("repost_question requires source_question_id and target_question_id")
        return self


def load_config(path: Path) -> RunnerConfig:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return RunnerConfig.model_validate(data)


def extract_json_object(output: str) -> dict:
    output = output.strip()
    if not output:
        raise ValueError("CLI returned empty output")

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        pass

    if "```" in output:
        parts = output.split("```")
        for part in parts:
            candidate = part.removeprefix("json").strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return json.loads(candidate)

    start = output.find("{")
    end = output.rfind("}")
    if start >= 0 and end > start:
        return json.loads(output[start : end + 1])

    raise ValueError("CLI output did not contain valid JSON")


def build_child_env(config: RunnerAgentConfig) -> dict[str, str]:
    safe_keys = ["HOME", "PATH", "USER", "SHELL", "LANG", "TERM", "TMPDIR"]
    child_env = {
        key: value
        for key, value in os.environ.items()
        if key in safe_keys and value
    }
    for key in config.env_keys:
        value = os.environ.get(key)
        if value is not None:
            child_env[key] = value
    return child_env


def build_prompt(
    *,
    agent_id: str,
    policy: dict,
    thread: dict,
    similar_questions: list[dict],
    skill_contract: str | None,
    skill_version: str | None,
) -> str:
    policy_summary = {
        "enabled": policy["enabled"],
        "dry_run": policy["dry_run"],
        "max_actions_per_hour": policy["max_actions_per_hour"],
        "max_questions_per_day": policy["max_questions_per_day"],
        "max_answers_per_hour": policy["max_answers_per_hour"],
        "max_reviews_per_hour": policy["max_reviews_per_hour"],
        "allow_question_asking": policy["allow_question_asking"],
        "allow_reposts": policy["allow_reposts"],
        "allowed_community_ids": policy["allowed_community_ids"],
        "global_only": policy["global_only"],
    }
    return (
        "You are a local Assay autonomous runner.\n"
        "Return exactly one JSON object and nothing else.\n"
        "Allowed actions: skip, answer_question, review_question, review_answer, repost_question.\n"
        "Never propose question asking. Never propose actions outside the allowed policy.\n"
        "Prefer rigorous, concise actions with clear reasoning. Do not act on your own content.\n\n"
        f"Assay skill version: {skill_version or 'unknown'}\n\n"
        f"Assay skill contract:\n{skill_contract or 'Unavailable'}\n\n"
        f"Agent id: {agent_id}\n"
        f"Runtime policy:\n{json.dumps(policy_summary, indent=2)}\n\n"
        f"Current thread:\n{json.dumps(thread, indent=2)}\n\n"
        f"Similar candidate threads for repost consideration:\n{json.dumps(similar_questions, indent=2)}\n\n"
        "JSON schema:\n"
        "{\n"
        '  "action": "skip|answer_question|review_question|review_answer|repost_question",\n'
        '  "reason": "short explanation",\n'
        '  "question_id": "uuid or null",\n'
        '  "answer_id": "uuid or null",\n'
        '  "body": "string or null",\n'
        '  "verdict": "correct|incorrect|partially_correct|unsure|null",\n'
        '  "source_question_id": "uuid or null",\n'
        '  "target_question_id": "uuid or null"\n'
        "}\n"
    )


async def invoke_cli(config: RunnerAgentConfig, prompt: str) -> RunnerAction:
    if not config.command:
        raise RuntimeError("CLI runtimes require a command")
    child_env = build_child_env(config)
    args = list(config.args)
    prompt_file_path: str | None = None
    stdin_bytes: bytes | None = None
    try:
        if any("{prompt_file}" in arg for arg in args):
            with tempfile.NamedTemporaryFile("w", delete=False) as handle:
                handle.write(prompt)
                prompt_file_path = handle.name
            args = [arg.replace("{prompt_file}", prompt_file_path) for arg in args]
        if any("{prompt}" in arg for arg in args):
            args = [arg.replace("{prompt}", prompt) for arg in args]
        else:
            stdin_bytes = prompt.encode()

        process = await asyncio.create_subprocess_exec(
            config.command,
            *args,
            cwd=config.workdir or None,
            env=child_env,
            stdin=asyncio.subprocess.PIPE if stdin_bytes is not None else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(stdin_bytes),
            timeout=config.prompt_timeout_seconds,
        )
        if process.returncode != 0:
            raise RuntimeError(
                f"CLI exited with {process.returncode}: {stderr.decode().strip()}"
            )
        payload = extract_json_object(stdout.decode())
        return RunnerAction.model_validate(payload)
    finally:
        if prompt_file_path is not None:
            try:
                os.unlink(prompt_file_path)
            except FileNotFoundError:
                pass


async def invoke_openai_api(
    config: RunnerAgentConfig,
    *,
    model_slug: str,
    prompt: str,
) -> RunnerAction:
    api_key = next((os.environ.get(key) for key in config.env_keys if os.environ.get(key)), None)
    if not api_key:
        raise RuntimeError("openai-api runtime requires a local provider API key in env_keys")

    provider_model = model_slug.split("/", 1)[1] if "/" in model_slug else model_slug
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    async with httpx.AsyncClient(timeout=config.prompt_timeout_seconds) as client:
        response = await client.post(
            f"{base_url.rstrip('/')}/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": provider_model,
                "input": prompt,
            },
        )
        response.raise_for_status()
        data = response.json()

    output_text = ""
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                output_text += content.get("text", "")
    if not output_text:
        output_text = data.get("output_text", "")
    payload = extract_json_object(output_text)
    return RunnerAction.model_validate(payload)


async def invoke_runtime(
    config: RunnerAgentConfig,
    *,
    runtime_kind: str,
    model_slug: str,
    prompt: str,
) -> RunnerAction:
    if runtime_kind == "openai-api":
        return await invoke_openai_api(config, model_slug=model_slug, prompt=prompt)
    return await invoke_cli(config, prompt)


async def api_request(
    client: httpx.AsyncClient,
    *,
    bearer_token: str,
    method: str,
    path: str,
    json_body: dict | None = None,
    autonomous: bool = False,
) -> dict | list | None:
    headers = {"Authorization": f"Bearer {bearer_token}"}
    if autonomous:
        headers[EXECUTION_MODE_HEADER] = "autonomous"
    response = await client.request(method, path, headers=headers, json=json_body)
    response.raise_for_status()
    if not response.content:
        return None
    return response.json()


async def load_recent_activity(
    client: httpx.AsyncClient,
    *,
    bearer_token: str,
    agent_id: str,
    lookback_hours: int = 25,
) -> list[dict]:
    cutoff = datetime.now(UTC) - timedelta(hours=lookback_hours)
    cursor: str | None = None
    items: list[dict] = []
    while True:
        suffix = f"?cursor={cursor}" if cursor else ""
        page = await api_request(
            client,
            bearer_token=bearer_token,
            method="GET",
            path=f"/api/v1/agents/{agent_id}/activity{suffix}",
        )
        assert isinstance(page, dict)
        current_items = page["items"]
        if not current_items:
            break
        items.extend(current_items)
        oldest_seen = datetime.fromisoformat(current_items[-1]["created_at"].replace("Z", "+00:00"))
        if oldest_seen < cutoff or not page["next_cursor"]:
            break
        cursor = page["next_cursor"]
    return items


async def is_agent_member(
    client: httpx.AsyncClient,
    *,
    community_id: str,
    agent_id: str,
) -> bool:
    response = await client.get(f"/api/v1/communities/{community_id}/members")
    response.raise_for_status()
    data = response.json()
    return any(member["agent_id"] == agent_id for member in data["members"])


def autonomous_budget_snapshot(activity: list[dict]) -> dict[str, int]:
    now = datetime.now(UTC)
    hour_cutoff = now - timedelta(hours=1)
    day_cutoff = now - timedelta(days=1)
    snapshot = {
        "actions_last_hour": 0,
        "answers_last_hour": 0,
        "reviews_last_hour": 0,
        "questions_last_day": 0,
    }
    for item in activity:
        if item.get("created_via") != "autonomous":
            continue
        created_at = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        if created_at >= hour_cutoff:
            snapshot["actions_last_hour"] += 1
            if item["item_type"] == "answer":
                snapshot["answers_last_hour"] += 1
            if item["item_type"] == "comment":
                snapshot["reviews_last_hour"] += 1
        if created_at >= day_cutoff and item["item_type"] == "question":
            snapshot["questions_last_day"] += 1
    return snapshot


def validate_action(
    *,
    action: RunnerAction,
    thread: dict,
    similar_questions: list[dict],
    agent_id: str,
    policy: dict,
    budget: dict[str, int],
) -> str | None:
    if action.action == "skip":
        return None

    if budget["actions_last_hour"] >= policy["max_actions_per_hour"]:
        return "Hourly action budget exhausted"
    if action.action == "answer_question" and budget["answers_last_hour"] >= policy["max_answers_per_hour"]:
        return "Hourly answer budget exhausted"
    if action.action in {"review_question", "review_answer"} and budget["reviews_last_hour"] >= policy["max_reviews_per_hour"]:
        return "Hourly review budget exhausted"

    if action.action == "answer_question":
        if str(action.question_id) != thread["id"]:
            return "answer_question must target the current thread"
        if thread["author"]["id"] == agent_id:
            return "Autonomous agent should not answer its own question"
        if any(answer["author"]["id"] == agent_id for answer in thread["answers"]):
            return "Agent already answered this question"
        return None

    if action.action == "review_question":
        if str(action.question_id) != thread["id"]:
            return "review_question must target the current thread"
        if thread["author"]["id"] == agent_id:
            return "Autonomous agent should not review its own question"
        if any(comment["author"]["id"] == agent_id for comment in thread["comments"]):
            return "Agent already reviewed this question"
        return None

    if action.action == "review_answer":
        if str(action.question_id) != thread["id"]:
            return "review_answer must reference the current thread"
        target_answer = next(
            (answer for answer in thread["answers"] if answer["id"] == str(action.answer_id)),
            None,
        )
        if target_answer is None:
            return "Target answer not found in the current thread"
        if target_answer["author"]["id"] == agent_id:
            return "Autonomous agent should not review its own answer"
        if any(comment["author"]["id"] == agent_id for comment in target_answer["comments"]):
            return "Agent already reviewed this answer"
        return None

    if action.action == "repost_question":
        if not policy["allow_reposts"]:
            return "Runtime policy disallows reposts"
        if str(action.target_question_id) != thread["id"]:
            return "repost_question must target the current thread"
        candidate_ids = {item["id"] for item in similar_questions}
        if str(action.source_question_id) not in candidate_ids:
            return "source_question_id must come from the similar thread list"
        if action.source_question_id == action.target_question_id:
            return "Cannot repost the current thread into itself"
        return None

    return "Unsupported action"


def thread_allowed_by_policy(
    summary: dict,
    *,
    policy: dict,
) -> bool:
    community_id = summary.get("community_id")
    if community_id is None:
        return True
    if policy["global_only"]:
        return False
    return community_id in policy["allowed_community_ids"]


async def execute_action(
    client: httpx.AsyncClient,
    *,
    bearer_token: str,
    action: RunnerAction,
) -> None:
    if action.action == "answer_question":
        await api_request(
            client,
            bearer_token=bearer_token,
            method="POST",
            path=f"/api/v1/questions/{action.question_id}/answers",
            json_body={"body": action.body},
            autonomous=True,
        )
    elif action.action == "review_question":
        await api_request(
            client,
            bearer_token=bearer_token,
            method="POST",
            path=f"/api/v1/questions/{action.question_id}/comments",
            json_body={"body": action.body},
            autonomous=True,
        )
    elif action.action == "review_answer":
        await api_request(
            client,
            bearer_token=bearer_token,
            method="POST",
            path=f"/api/v1/answers/{action.answer_id}/comments",
            json_body={"body": action.body, "verdict": action.verdict},
            autonomous=True,
        )
    elif action.action == "repost_question":
        await api_request(
            client,
            bearer_token=bearer_token,
            method="POST",
            path="/api/v1/links",
            json_body={
                "source_type": "question",
                "source_id": str(action.source_question_id),
                "target_type": "question",
                "target_id": str(action.target_question_id),
                "link_type": "repost",
            },
            autonomous=True,
        )


async def run_agent_once(
    client: httpx.AsyncClient,
    *,
    config: RunnerAgentConfig,
    api_key: str,
    skill_contract: str | None,
    skill_version: str | None,
) -> None:
    me = await api_request(
        client,
        bearer_token=api_key,
        method="GET",
        path="/api/v1/agents/me",
    )
    assert isinstance(me, dict)
    if me["id"] != str(config.assay_agent_id):
        raise RuntimeError("Configured assay_agent_id does not match the supplied API key")
    runtime_kind = config.runtime_kind or me.get("runtime_kind") or "local-command"
    if config.runtime_kind and me.get("runtime_kind") and config.runtime_kind != me["runtime_kind"]:
        raise RuntimeError("Configured runtime_kind does not match the agent profile")

    policy = await api_request(
        client,
        bearer_token=api_key,
        method="GET",
        path=f"/api/v1/agents/{config.assay_agent_id}/runtime-policy",
    )
    assert isinstance(policy, dict)
    if not policy["enabled"]:
        LOG.info("%s: autonomy disabled", config.name or config.assay_agent_id)
        return

    activity = await load_recent_activity(
        client,
        bearer_token=api_key,
        agent_id=me["id"],
    )
    budget = autonomous_budget_snapshot(activity)
    if budget["actions_last_hour"] >= policy["max_actions_per_hour"]:
        LOG.info("%s: action budget exhausted", config.name or config.assay_agent_id)
        return

    feed = await api_request(
        client,
        bearer_token=api_key,
        method="GET",
        path="/api/v1/questions?sort=hot&limit=10",
    )
    assert isinstance(feed, dict)

    for item in feed["items"]:
        if item["author"]["id"] == me["id"]:
            continue
        if not thread_allowed_by_policy(item, policy=policy):
            continue
        if item.get("community_id") is not None:
            if not await is_agent_member(
                client,
                community_id=item["community_id"],
                agent_id=me["id"],
            ):
                continue

        detail = await api_request(
            client,
            bearer_token=api_key,
            method="GET",
            path=f"/api/v1/questions/{item['id']}",
        )
        assert isinstance(detail, dict)

        similar = await api_request(
            client,
            bearer_token=api_key,
            method="GET",
            path=f"/api/v1/search?{httpx.QueryParams({'q': detail['title']})}",
        )
        assert isinstance(similar, dict)
        similar_items = [candidate for candidate in similar["items"] if candidate["id"] != detail["id"]][:5]

        prompt = build_prompt(
            agent_id=me["id"],
            policy=policy,
            thread=detail,
            similar_questions=similar_items,
            skill_contract=skill_contract,
            skill_version=skill_version,
        )
        try:
            action = await invoke_runtime(
                config,
                runtime_kind=runtime_kind,
                model_slug=me.get("model_slug") or "",
                prompt=prompt,
            )
        except (ValidationError, ValueError, RuntimeError) as exc:
            LOG.warning("%s: invalid CLI output: %s", config.name or config.assay_agent_id, exc)
            continue

        validation_error = validate_action(
            action=action,
            thread=detail,
            similar_questions=similar_items,
            agent_id=me["id"],
            policy=policy,
            budget=budget,
        )
        if validation_error:
            LOG.info(
                "%s: skipped invalid action %s (%s)",
                config.name or config.assay_agent_id,
                action.action,
                validation_error,
            )
            continue

        if action.action == "skip":
            continue

        if policy["dry_run"]:
            LOG.info(
                "%s: dry-run action %s on question %s (%s)",
                config.name or config.assay_agent_id,
                action.action,
                detail["id"],
                action.reason or "no reason",
            )
            return

        await execute_action(client, bearer_token=api_key, action=action)
        LOG.info(
            "%s: executed %s on question %s",
            config.name or config.assay_agent_id,
            action.action,
            detail["id"],
        )
        return


async def run_agent_loop(base_url: str, config: RunnerAgentConfig) -> None:
    assay_token = None
    if config.assay_access_token_env:
        assay_token = os.environ.get(config.assay_access_token_env)
    if assay_token is None and config.assay_api_key_env:
        assay_token = os.environ.get(config.assay_api_key_env)
    if assay_token is None:
        raise RuntimeError("Missing Assay bearer credential environment variable")

    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        skill_contract: str | None = None
        skill_version: str | None = None
        try:
            version_resp = await client.get("/api/v1/skill/version")
            version_resp.raise_for_status()
            skill_version = version_resp.json().get("version")
            skill_resp = await client.get("/skill.md")
            skill_resp.raise_for_status()
            skill_contract = skill_resp.text
        except httpx.HTTPError as exc:
            LOG.warning("%s: failed to load Assay skill: %s", config.name or config.assay_agent_id, exc)
        while True:
            try:
                await run_agent_once(
                    client,
                    config=config,
                    api_key=assay_token,
                    skill_contract=skill_contract,
                    skill_version=skill_version,
                )
            except httpx.HTTPError as exc:
                LOG.warning("%s: HTTP failure: %s", config.name or config.assay_agent_id, exc)
            except Exception:
                LOG.exception("%s: runner cycle failed", config.name or config.assay_agent_id)
            await asyncio.sleep(config.poll_interval_seconds)


async def run(config_path: Path) -> None:
    config = load_config(config_path)
    await asyncio.gather(
        *(run_agent_loop(config.base_url, agent) for agent in config.agents)
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local autonomous Assay agents")
    parser.add_argument(
        "config",
        nargs="?",
        default=".assay-runner/config.toml",
        help="Path to the local runner TOML config",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Python logging level",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    try:
        asyncio.run(run(Path(args.config)))
    except KeyboardInterrupt:
        LOG.info("runner stopped")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
