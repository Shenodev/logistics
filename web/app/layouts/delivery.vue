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
  <div class="min-h-dvh bg-background text-foreground">
    <header class="sticky top-0 z-20 border-b border-outline-variant bg-surface-low/95 backdrop-blur">
      <div class="mx-auto flex max-w-md items-center justify-between gap-3 px-4 py-2.5">
        <div class="flex min-h-12 items-center gap-2.5">
          <div class="flex size-10 shrink-0 items-center justify-center rounded-lg border border-primary/30 bg-surface-container">
            <img src="/logo-icon.png" alt="ShenoFlow logo" class="h-6 w-6 shrink-0 object-contain" />
          </div>
          <div class="min-w-0">
            <p class="font-heading font-bold leading-tight tracking-tight text-on-surface">ShenoFlow</p>
            <p class="text-xs text-on-surface-variant">Delivery Driver</p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <span class="inline-flex min-h-8 items-center gap-1.5 rounded-full border border-primary/40 bg-primary/10 px-3 text-xs font-semibold text-primary">
            <span class="relative flex h-2 w-2">
              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
              <span class="relative inline-flex h-2 w-2 rounded-full bg-primary" />
            </span>
            Online
          </span>
          <button
            class="flex min-h-12 min-w-12 items-center justify-center rounded-lg text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary"
            type="button"
            title="Sign out"
            aria-label="Sign out"
            @click="logout"
          >
            <MIcon name="logout" class="text-[22px]" />
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto w-full max-w-md px-4 py-4 pb-28">
      <slot />
    </main>

    <nav
      class="fixed inset-x-0 bottom-0 z-20 border-t border-outline-variant bg-surface-low pb-[env(safe-area-inset-bottom)]"
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