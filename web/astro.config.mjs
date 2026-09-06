// @ts-check
import { defineConfig } from 'astro/config';

const publicSiteUrl = process.env.PUBLIC_SITE_URL?.trim();

// Static output; no adapter. The analysis repo stays the source of truth;
// this app only reads artifacts at build time. Watch scope is web/ only.
export default defineConfig({
  ...(publicSiteUrl ? { site: publicSiteUrl } : {}),
  output: 'static',
  vite: {
    server: {
      // Never watch the repo root: thousands of generated artifacts live there.
      watch: {
        ignored: ['**/analysis/**', '**/raw/**', '**/screenshots/**', '**/.git/**'],
      },
    },
  },
});
