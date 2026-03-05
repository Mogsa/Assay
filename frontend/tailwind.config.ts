import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        xbg: {
          primary: "#000000",
          secondary: "#16181C",
          hover: "#1D1F23",
        },
        xborder: "#2F3336",
        xtext: {
          primary: "#E7E9EA",
          secondary: "#71767B",
        },
        xaccent: {
          DEFAULT: "#1D9BF0",
          hover: "#1A8CD8",
        },
        xdanger: "#F4212E",
        xsuccess: "#00BA7C",
      },
    },
  },
  plugins: [],
};
export default config;
