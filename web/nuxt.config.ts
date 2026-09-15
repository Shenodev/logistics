// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/assets/css/tailwind.css'],
  modules: ['shadcn-nuxt', '@pinia/nuxt'],
  shadcn: {
    prefix: '',
    componentDir: '@/components/ui',
  },
  runtimeConfig: {
    public: {
      appDomain: 'logistics.shenodev.tech',
      adminSubdomain: 'admin',
      apiBase: '',
    },
    auth: {
      sessionSecret: 'shenoflow-dev-secret-change-me',
      sessionTtlSeconds: 60 * 60 * 24 * 7,
      cookieSecure: true,
      devAdminEmail: 'admin@sheno.dev',
      devAdminPassword: 'admin123',
      devUserEmail: 'user@sheno.dev',
      devUserPassword: 'user123',
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