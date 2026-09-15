<script setup lang="ts">
const { public: { siteUrl } } = useRuntimeConfig()

useHead({
  htmlAttrs: { lang: 'en', class: 'dark' },
  titleTemplate: '%s · ShenoFlow',
  meta: [
    { name: 'description', content: 'ShenoFlow — B2B logistics portal for fleet, dispatch, and shipment tracking across the Sheno logistics network.' },
    { name: 'theme-color', content: '#0f172a' },
    { property: 'og:site_name', content: 'ShenoFlow' },
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: 'ShenoFlow — B2B Logistics Portal' },
    { property: 'og:description', content: 'ShenoFlow — B2B logistics portal for fleet, dispatch, and shipment tracking across the Sheno logistics network.' },
    { property: 'og:image', content: `${siteUrl}/logo-icon.png` },
    { name: 'twitter:card', content: 'summary' },
    { name: 'twitter:title', content: 'ShenoFlow — B2B Logistics Portal' },
    { name: 'twitter:description', content: 'ShenoFlow — B2B logistics portal for fleet, dispatch, and shipment tracking across the Sheno logistics network.' },
    { name: 'twitter:image', content: `${siteUrl}/logo-icon.png` },
  ],
  link: [
    { rel: 'shortcut icon', type: 'image/x-icon', href: '/favicon.ico' },
    { rel: 'icon', type: 'image/png', href: '/logo-icon.png' },
    { rel: 'apple-touch-icon', href: '/logo-icon.png' },
  ],
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>