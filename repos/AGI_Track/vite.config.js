import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Deploying to GitHub Pages under a repo
  base: '/AGI_Track/',
  server: {
    port: 5173
  }
})
