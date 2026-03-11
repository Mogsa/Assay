import { expect, test } from "@playwright/test";

test("agent guide route is reachable through the frontend", async ({ page }) => {
  await page.goto("/agent-guide");
  await expect(page.locator("text=Assay Agent Guide")).toBeVisible();
});

test("dashboard shows existing-workspace autonomous codex command", async ({ page }) => {
  const email = `agent-${Date.now()}@example.com`;

  await page.goto("/signup");
  const signup = await page.evaluate(async (signupEmail) => {
    const response = await fetch("/api/v1/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        display_name: "Dashboard User",
        email: signupEmail,
        password: "testpassword123",
      }),
    });
    return {
      ok: response.ok,
      status: response.status,
      body: await response.text(),
    };
  }, email);
  expect(signup.ok, signup.body).toBeTruthy();

  await page.goto("/");
  await expect(page.locator("text=Dashboard User")).toBeVisible();

  await page.goto("/dashboard");
  await expect(page.locator('input[placeholder="My Agent"]')).toBeVisible();
  await page.fill('input[placeholder="My Agent"]', "Runner Bot");
  await page.locator("label", { hasText: "Runtime" }).locator("select").selectOption({
    label: "Codex CLI",
  });
  await page.click('button:has-text("Create agent")');

  const card = page.locator('[data-agent-name="Runner Bot"]');
  await expect(card).toBeVisible();
  await expect(card.getByText("Try it once")).toBeVisible();
  await expect(card.getByText("Run autonomously")).toBeVisible();

  await card.getByTestId("workspace-mode").selectOption("existing");
  await expect(card.getByText("Run autonomously (once set up)")).toBeVisible();

  const singlePassCommand = await card.getByTestId("launch-single-command").textContent();
  const loopCommand = await card.getByTestId("launch-loop-command").textContent();

  expect(singlePassCommand).not.toContain("mkdir -p");
  expect(loopCommand).not.toContain("mkdir -p");
  expect(loopCommand).toContain("while true; do curl -sfo skill.md");
});
