// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/assets/css/tailwind.css'],
  app: {
    head: {
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'icon', type: 'image/png', href: '/logo-icon.png' },
      ],
    },
  },
  modules: ['shadcn-nuxt', '@pinia/nuxt'],
  shadcn: {
    prefix: '',
    componentDir: '@/components/ui',
  },
  runtimeConfig: {
    public: {
      appDomain: 'logistics.shenodev.tech',
      adminSubdomain: 'admin',
      apiBase: 'http://localhost:8000',
    },
  },
  vite: {
    plugins: [
      tailwindcss(),
    ],
    server: {
      allowedHosts: ['logistics.shenodev.tech', 'admin.logistics.shenodev.tech', '.shenodev.tech', 'localhost'],
    },
  },
})