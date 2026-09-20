import { defineConfig } from 'vitest/config'
import { resolve } from 'path'

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['tests/**/*.test.ts', 'app/**/*.test.ts'],
  },
  resolve: {
    alias: {
      '~': resolve(__dirname, './app'),
      '~~': resolve(__dirname, './'),
      '@': resolve(__dirname, './app'),
    },
  },
})
