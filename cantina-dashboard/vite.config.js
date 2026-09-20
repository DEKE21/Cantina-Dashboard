import {svelte} from '@sveltejs/vite-plugin-svelte';
import tailwindcss from '@tailwindcss/vite';
import {defineConfig} from 'vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [tailwindcss(), svelte()],
  optimizeDeps: {
    exclude: [
      '@tailwindcss/oxide', '@tailwindcss/oxide-win32-x64-msvc', 'tailwindcss'
    ]
  }
});
