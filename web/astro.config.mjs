// @ts-check
import { defineConfig } from 'astro/config';

// Static output; no adapter. The analysis repo stays the source of truth;
// this app only reads artifacts at build time. Watch scope is web/ only.
export default defineConfig({
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
