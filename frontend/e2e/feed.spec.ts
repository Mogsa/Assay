import { expect, test } from "@playwright/test";

test("feed page loads with main feed controls", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("text=Main Feed")).toBeVisible();
  await expect(page.locator('select')).toBeVisible();
});

test("feed is publicly readable", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("text=Browse questions, answers, and reviews")).toBeVisible();
});
