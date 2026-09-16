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
        { name: 'theme-color', content: '#0F172A' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
        { name: 'apple-mobile-web-app-title', content: 'ShenoFlow Delivery' },
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'icon', type: 'image/png', sizes: '48x48', href: '/favicon-48x48.png' },
        { rel: 'icon', type: 'image/png', sizes: '96x96', href: '/favicon-96x96.png' },
        { rel: 'icon', type: 'image/png', sizes: '144x144', href: '/favicon-144x144.png' },
        { rel: 'icon', type: 'image/png', sizes: '192x192', href: '/favicon-192x192.png' },
        { rel: 'icon', type: 'image/png', sizes: '512x512', href: '/favicon-512x512.png' },
        { rel: 'apple-touch-icon', sizes: '192x192', href: '/favicon-192x192.png' },
      ],
    },
  },
  modules: ['shadcn-nuxt', '@pinia/nuxt', '@vite-pwa/nuxt'],
  shadcn: {
    prefix: '',
    componentDir: '@/components/ui',
  },
  pwa: {
    registerType: 'autoUpdate',
    includeAssets: ['favicon.ico', 'logo-icon.png'],
    manifest: {
      name: 'ShenoFlow Delivery',
      short_name: 'ShenoFlow',
      description: 'Mobile-first delivery PWA for ShenoFlow drivers — accept orders, navigate, and update status on the go.',
      lang: 'en',
      theme_color: '#0F172A',
      background_color: '#0F172A',
      display: 'standalone',
      orientation: 'portrait',
      scope: '/',
      start_url: '/',
      categories: ['business', 'productivity', 'navigation'],
      prefer_related_applications: false,
      shortcuts: [
        {
          name: 'Active Orders',
          short_name: 'Orders',
          url: '/orders',
          icons: [{ src: '/favicon-192x192.png', sizes: '192x192', type: 'image/png' }],
        },
      ],
      icons: [
        { src: '/favicon-48x48.png', sizes: '48x48', type: 'image/png' },
        { src: '/favicon-96x96.png', sizes: '96x96', type: 'image/png' },
        { src: '/favicon-144x144.png', sizes: '144x144', type: 'image/png' },
        { src: '/favicon-192x192.png', sizes: '192x192', type: 'image/png' },
        { src: '/favicon-512x512.png', sizes: '512x512', type: 'image/png' },
        { src: '/favicon-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
      ],
    },
    workbox: {
      globPatterns: ['**/*.{js,css,html,ico,png,svg,ttf,woff,woff2}'],
      navigateFallback: '/index.html',
      navigateFallbackDenylist: [/^\/(?:api|login|signup)\//],
      runtimeCaching: [
        {
          urlPattern: /\/_nuxt\/.*\.(?:js|css)$/,
          handler: 'StaleWhileRevalidate',
          options: {
            cacheName: 'shenoflow-app-shell',
            expiration: { maxEntries: 60, maxAgeSeconds: 60 * 60 * 24 * 30 },
          },
        },
      ],
    },
    devOptions: {
      enabled: false,
    },
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