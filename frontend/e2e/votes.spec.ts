import { test, expect } from "@playwright/test";

test("question, answer, and comment voting flows stay interactive", async ({ page }) => {
  const authorEmail = `author-${Date.now()}@example.com`;
  const voterEmail = `voter-${Date.now()}@example.com`;

  await page.goto("/signup");
  await page.fill('input[placeholder="Display name"]', "Author");
  await page.fill('input[placeholder="Email"]', authorEmail);
  await page.fill('input[type="password"]', "testpassword123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/");

  await page.click("text=Ask Question");
  await page.fill('input[id="title"]', "Vote semantics smoke test");
  await page.fill('textarea[id="body"]', "Checking vote toggle and switch behavior.");
  await page.click('button:has-text("Post Question")');
  await expect(page.locator("h1")).toHaveText("Vote semantics smoke test");

  await page.fill('textarea[placeholder="Write your answer…"]', "Author answer body");
  await page.click('button:has-text("Post Answer")');

  await page.locator("button", { hasText: "Add a comment" }).first().click();
  await page.locator('textarea[placeholder="Add a comment…"]').first().fill("Author question comment");
  await page.click('button:has-text("Comment")');

  const questionUrl = page.url();
  await page.click("text=Log out");

  await page.goto("/signup");
  await page.fill('input[placeholder="Display name"]', "Voter");
  await page.fill('input[placeholder="Email"]', voterEmail);
  await page.fill('input[type="password"]', "testpassword123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/");

  await page.goto(questionUrl);

  const upvotes = page.getByLabel("Upvote");
  const downvotes = page.getByLabel("Downvote");

  await upvotes.first().click();
  await upvotes.first().click();
  await downvotes.first().click();
  await expect(downvotes.first()).toHaveClass(/text-red-600/);

  await upvotes.nth(1).click();
  await expect(upvotes.nth(1)).toHaveClass(/text-green-600/);

  const commentUpvote = page.getByLabel("Upvote comment").first();
  await commentUpvote.click();
  await expect(commentUpvote).toHaveClass(/text-green-600/);
});
