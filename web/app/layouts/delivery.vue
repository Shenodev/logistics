<script setup lang="ts">
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const nav = [
  { label: 'Incoming', icon: 'inbox', to: '/incoming' },
  { label: 'Orders', icon: 'local_shipping', to: '/orders' },
  { label: 'Wallet', icon: 'account_balance_wallet', to: '/wallet' },
  { label: 'Profile', icon: 'person', to: '/profile' },
]

function isActive(to: string) {
  return route.path === to || route.path.startsWith(`${to}/`)
}

async function logout() {
  await auth.logout()
  await router.push('/login')
}
</script>

<template>
  <div class="min-h-dvh bg-background text-foreground lg:flex">
    <!-- Desktop sidebar — hidden on mobile -->
    <aside class="hidden lg:flex lg:fixed lg:inset-y-0 lg:left-0 lg:z-30 lg:w-64 lg:flex-col lg:border-r lg:border-outline-variant lg:bg-surface-low">
      <div class="flex h-16 items-center gap-2.5 border-b border-outline-variant px-5">
        <div class="flex size-9 items-center justify-center rounded-lg border border-primary/30 bg-surface-container">
          <img src="/logo-icon.png" alt="ShenoFlow logo" class="h-5 w-5 object-contain" />
        </div>
        <div class="min-w-0">
          <p class="font-heading text-sm font-bold leading-none tracking-tight text-on-surface">ShenoFlow</p>
          <p class="text-xs text-on-surface-variant">Delivery Driver</p>
        </div>
        <span class="ml-auto inline-flex items-center gap-1 rounded-full border border-primary/30 bg-primary/10 px-2 py-0.5 text-[11px] font-bold text-primary">
          <span class="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" /> Online
        </span>
      </div>
      <nav class="flex-1 space-y-1 p-3" aria-label="Driver navigation desktop">
        <NuxtLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors"
          :class="isActive(item.to) ? 'bg-surface-container-high border border-outline-variant text-primary' : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'"
        >
          <MIcon :name="item.icon" :filled="isActive(item.to)" class="text-[20px]" />
          {{ item.label }}
          <MIcon v-if="isActive(item.to)" name="chevron_right" class="ml-auto text-[18px] opacity-60" />
        </NuxtLink>
      </nav>
      <div class="border-t border-outline-variant p-3">
        <div class="rounded-xl border border-outline-variant bg-surface-container p-3">
          <p class="text-xs font-semibold uppercase tracking-wider text-on-surface-variant">Driver mode</p>
          <p class="mt-1 text-sm text-on-surface">Large touch targets • Outdoor readable</p>
        </div>
        <button class="mt-3 flex w-full items-center justify-center gap-1.5 rounded-xl border border-outline-variant bg-surface-container-high px-3 py-2.5 text-sm font-semibold text-on-surface-variant hover:text-primary" @click="logout">
          <MIcon name="logout" class="text-[18px]" /> Sign out
        </button>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col lg:ml-64">
      <header class="sticky top-0 z-20 border-b border-outline-variant bg-surface-low/95 backdrop-blur">
        <div class="mx-auto flex max-w-md items-center justify-between gap-3 px-4 py-2.5 lg:mx-0 lg:max-w-none lg:px-6 xl:px-8">
          <div class="flex min-h-12 items-center gap-2.5">
            <div class="flex size-10 shrink-0 items-center justify-center rounded-lg border border-primary/30 bg-surface-container lg:hidden">
              <img src="/logo-icon.png" alt="ShenoFlow logo" class="h-6 w-6 shrink-0 object-contain" />
            </div>
            <div class="min-w-0">
              <p class="font-heading font-bold leading-tight tracking-tight text-on-surface lg:text-[15px]">ShenoFlow</p>
              <p class="text-xs text-on-surface-variant">Delivery Driver</p>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <span class="inline-flex min-h-8 items-center gap-1.5 rounded-full border border-primary/40 bg-primary/10 px-3 text-xs font-semibold text-primary lg:hidden">
              <span class="relative flex h-2 w-2">
                <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
                <span class="relative inline-flex h-2 w-2 rounded-full bg-primary" />
              </span>
              Online
            </span>
            <span class="hidden lg:inline-flex items-center gap-2 rounded-full border border-outline-variant bg-surface-container px-3 py-1.5 text-xs font-medium text-on-surface-variant">
              <MIcon name="verified" class="text-[14px] text-primary" /> PWA offline-ready
            </span>
            <button
              class="flex min-h-12 min-w-12 items-center justify-center rounded-lg text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary lg:hidden"
              type="button"
              title="Sign out"
              aria-label="Sign out"
              @click="logout"
            >
              <MIcon name="logout" class="text-[22px]" />
            </button>
            <button class="hidden lg:inline-flex min-h-9 items-center gap-1.5 rounded-xl border border-outline-variant bg-surface-container px-3 text-sm font-semibold text-on-surface-variant hover:text-primary" @click="logout">
              <MIcon name="logout" class="text-[16px]" /> Sign out
            </button>
          </div>
        </div>
      </header>

      <main class="mx-auto w-full max-w-md px-4 py-4 pb-28 lg:mx-0 lg:max-w-none lg:px-6 lg:py-6 lg:pb-6 xl:px-8">
        <div class="mx-auto w-full max-w-md lg:max-w-5xl xl:max-w-6xl">
          <slot />
        </div>
      </main>
    </div>

    <nav
      class="fixed inset-x-0 bottom-0 z-20 border-t border-outline-variant bg-surface-low pb-[env(safe-area-inset-bottom)] lg:hidden"
      aria-label="Driver navigation"
    >
      <div class="mx-auto flex max-w-md items-stretch justify-between">
        <NuxtLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="flex min-h-16 flex-1 flex-col items-center justify-center gap-0.5 transition-colors"
          :class="isActive(item.to)
            ? 'text-primary'
            : 'text-on-surface-variant hover:text-on-surface'"
          :aria-current="isActive(item.to) ? 'page' : undefined"
        >
          <span
            class="flex h-1 w-8 rounded-full"
            :class="isActive(item.to) ? 'bg-primary' : 'bg-transparent'"
          />
          <MIcon :name="item.icon" :filled="isActive(item.to)" class="text-[22px]" />
          <span class="text-[11px] font-semibold tracking-wide">{{ item.label }}</span>
        </NuxtLink>
      </div>
    </nav>
  </div>
</template>