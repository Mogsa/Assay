import { test, expect } from "@playwright/test";

test("feed page loads with sort tabs", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("text=Hot")).toBeVisible();
  await expect(page.locator("text=Open")).toBeVisible();
  await expect(page.locator("text=New")).toBeVisible();
});
