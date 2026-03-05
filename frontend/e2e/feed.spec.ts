import { test, expect } from "@playwright/test";

test("feed page loads with sort tabs", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("text=Hot")).toBeVisible();
  await expect(page.locator("text=Open")).toBeVisible();
  await expect(page.locator("text=New")).toBeVisible();
});

test("unauthorized feed shows login-required message", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("text=Log in required to view questions.")).toBeVisible();
  await expect(page.locator('a:has-text("Go to login")')).toBeVisible();
});
