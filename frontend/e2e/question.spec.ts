import { test, expect } from "@playwright/test";

test("create and view question", async ({ page }) => {
  const email = `test-${Date.now()}@example.com`;

  await page.goto("/signup");
  await page.fill('input[placeholder="Display name"]', "Question Asker");
  await page.fill('input[placeholder="Email"]', email);
  await page.fill('input[type="password"]', "testpassword123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/");

  await page.click("text=Ask Question");
  await page.fill('input[id="title"]', "Is P = NP?");
  await page.fill('textarea[id="body"]', "Has anyone proven this yet? Asking for a friend.");
  await page.click('button:has-text("Post Question")');

  await expect(page.locator("h1")).toHaveText("Is P = NP?");
  await expect(page.locator("text=Has anyone proven this yet?")).toBeVisible();
});
