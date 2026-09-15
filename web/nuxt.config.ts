// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/assets/css/tailwind.css'],
  app: {
    head: {
      title: 'ShenoFlow',
      meta: [
        { name: 'description', content: 'ShenoFlow — B2B logistics portal for fleet, dispatch, and shipment tracking.' },
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
      apiBase: 'https://api.logistics.shenodev.tech',
      siteUrl: 'https://logistics.shenodev.tech',
      stripePk: '',
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