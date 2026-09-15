<script setup lang="ts">
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const searchQuery = ref('')

const initials = computed(() => {
  const name = auth.user?.name?.trim() || 'Sh'
  return name
    .split(/\s+/)
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
})

const nav = [
  { label: 'Overview', icon: 'dashboard', to: '/' },
  { label: 'My Shipments', icon: 'local_shipping', to: '/shipments' },
  { label: 'Billing', icon: 'receipt_long', to: '/billing' },
  { label: 'Profile', icon: 'account_circle', to: '/profile' },
]

const footerNav = [
  { label: 'Support', icon: 'help', to: '/profile' },
  { label: 'Settings', icon: 'settings', to: '/profile' },
]

function isActive(to: string) {
  if (to === '/') return route.path === '/'
  return route.path === to || route.path.startsWith(`${to}/`)
}

function submitSearch() {
  const query = searchQuery.value.trim()
  if (!query) return
  router.push(`/shipments/${encodeURIComponent(query)}`)
}

async function logout() {
  await auth.logout()
  await router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <aside class="fixed top-0 left-0 z-40 flex h-screen w-64 flex-col justify-between border-r border-sidebar-border bg-surface-low">
      <div class="flex h-full flex-col justify-between p-4">
        <div>
          <div class="mb-6 flex items-center gap-2 px-1 py-2">
            <div class="flex size-8 items-center justify-center rounded-lg border border-primary/30 bg-surface-container">
              <img
                src="/logo-icon.png"
                alt="ShenoFlow logo"
                class="h-5 w-5 shrink-0 object-contain"
              />
            </div>
            <div>
              <p class="font-heading text-headline-sm leading-none font-bold tracking-tight text-on-surface">ShenoFlow</p>
              <p class="mt-0.5 text-label-sm text-on-surface-variant">Shipper Enterprise Portal</p>
            </div>
          </div>

          <Button
            class="mb-6 w-full items-center justify-center gap-1 rounded-lg bg-primary-container py-2.5 font-label-md font-semibold text-on-primary-container transition-colors duration-150 hover:bg-primary active:scale-[0.98]"
            as-child
          >
            <NuxtLink to="/shipments">
              <MIcon name="add" class="text-[18px]" />
              <span>New Shipment</span>
            </NuxtLink>
          </Button>

          <nav class="space-y-1">
            <NuxtLink
              v-for="item in nav"
              :key="item.to"
              :to="item.to"
              class="flex items-center gap-2 rounded-r-lg px-4 py-2 text-label-md transition-colors duration-150"
              :class="isActive(item.to)
                ? 'border-l-2 border-primary bg-surface-container-highest font-label-md text-primary'
                : 'font-label-md text-on-surface-variant hover:bg-surface-high hover:text-on-surface'"
            >
              <MIcon :name="item.icon" :filled="isActive(item.to) && item.to === '/shipments'" class="text-[20px]" />
              <span>{{ item.label }}</span>
            </NuxtLink>
          </nav>
        </div>

        <div class="space-y-4 border-t border-outline-variant pt-4">
          <nav class="space-y-1">
            <NuxtLink
              v-for="item in footerNav"
              :key="item.label"
              :to="item.to"
              class="flex items-center gap-2 rounded-r-lg px-4 py-1.5 font-label-md text-on-surface-variant transition-colors duration-150 hover:bg-surface-high hover:text-on-surface"
            >
              <MIcon :name="item.icon" class="text-[20px]" />
              <span>{{ item.label }}</span>
            </NuxtLink>
          </nav>

          <div class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-container p-2">
            <div class="flex items-center gap-1">
              <span class="relative flex h-2 w-2">
                <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
                <span class="relative inline-flex h-2 w-2 rounded-full bg-primary" />
              </span>
              <span class="text-label-sm text-on-surface-variant">Telemetry Active</span>
            </div>
            <span class="text-label-sm font-semibold text-primary">99.98%</span>
          </div>

          <div class="flex items-center gap-2 p-1">
            <div class="flex size-9 items-center justify-center rounded-full border border-outline-variant bg-surface-container-highest text-label-md font-bold text-primary">
              {{ initials }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-label-md font-medium text-on-surface">{{ auth.user?.name }}</p>
              <p class="truncate text-label-sm text-on-surface-variant">{{ auth.user?.email }}</p>
            </div>
            <button
              class="rounded-lg p-1.5 text-outline transition-colors hover:text-primary"
              title="Sign out"
              @click="logout"
            >
              <MIcon name="logout" class="text-[18px]" />
            </button>
          </div>
        </div>
      </div>
    </aside>

    <header class="fixed top-0 right-0 left-64 z-30 flex h-16 items-center justify-between border-b border-outline-variant bg-surface-low px-6">
      <div class="flex max-w-xl flex-1 items-center gap-4">
        <div class="relative w-full">
          <MIcon name="search" class="absolute top-1/2 left-3 -translate-y-1/2 text-[18px] text-outline" />
          <input
            v-model="searchQuery"
            class="w-full rounded-lg border border-outline-variant bg-surface py-1.5 pr-4 pl-9 font-body-md text-body-md text-on-surface transition-colors placeholder:text-outline focus:border-primary focus:outline-none"
            type="text"
            placeholder="Search shipments, vessels, manifests..."
            @keyup.enter="submitSearch"
          />
        </div>
      </div>

      <div class="flex items-center gap-4">
        <button class="rounded-lg p-1.5 text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary" title="Notifications">
          <MIcon name="notifications" class="text-[20px]" />
        </button>
        <NuxtLink to="/profile" class="rounded-lg p-1.5 text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary" title="Help">
          <MIcon name="help_outline" class="text-[20px]" />
        </NuxtLink>
        <div class="hidden h-5 w-px bg-outline-variant" />
        <span class="hidden text-label-md text-on-surface-variant lg:inline-block">Shipper Enterprise Portal</span>
        <Button
          class="flex items-center gap-1 rounded-lg bg-secondary-container px-4 py-1.5 font-label-md font-semibold text-on-secondary-container transition-colors hover:bg-secondary-container hover:opacity-90"
          size="sm"
          as-child
        >
          <NuxtLink to="/shipments">
            <MIcon name="add_circle" class="text-[16px]" />
            <span>Create Booking</span>
          </NuxtLink>
        </Button>
      </div>
    </header>

    <div class="ml-64 min-h-screen pt-16">
      <slot />

      <footer class="py-4 text-center text-xs text-muted-foreground">
        Sheno B2B Logistics
      </footer>
    </div>
  </div>
</template>