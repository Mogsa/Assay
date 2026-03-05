import { test, expect } from "@playwright/test";

test("signup and login flow", async ({ page }) => {
  const email = `test-${Date.now()}@example.com`;

  await page.goto("/signup");
  await page.fill('input[placeholder="Display name"]', "Test User");
  await page.fill('input[placeholder="Email"]', email);
  await page.fill('input[type="password"]', "testpassword123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/");
  await expect(page.locator("text=Test User")).toBeVisible();

  await page.click("text=Log out");
  await expect(page.locator("text=Log in")).toBeVisible();

  await page.goto("/login");
  await page.fill('input[placeholder="Email"]', email);
  await page.fill('input[type="password"]', "testpassword123");
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL("/");
  await expect(page.locator("text=Test User")).toBeVisible();
});

test("profile route while logged out shows login prompt", async ({ page }) => {
  await page.goto("/profile/00000000-0000-0000-0000-000000000000");
  await expect(page.locator("text=Log in required to view profiles.")).toBeVisible();
  await expect(page.locator('a:has-text("Go to login")')).toBeVisible();
});
