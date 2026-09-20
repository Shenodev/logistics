<script setup lang="ts">
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const searchQuery = ref('')
const mobileOpen = ref(false)

watch(() => route.fullPath, () => {
  mobileOpen.value = false
})

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
    <div
      v-if="mobileOpen"
      class="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm lg:hidden"
      aria-hidden="true"
      @click="mobileOpen = false"
    />
    <aside
      class="fixed top-0 left-0 z-40 flex h-screen w-64 flex-col justify-between border-r border-sidebar-border bg-surface-low transition-transform duration-200 ease-in-out lg:translate-x-0"
      :class="mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
    >
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

          <nav class="mb-6 space-y-1">
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

    <header class="fixed top-0 right-0 left-0 z-20 flex h-16 items-center justify-between border-b border-outline-variant bg-surface-low px-4 lg:left-64 lg:px-6">
      <div class="flex min-w-0 flex-1 items-center gap-3 lg:max-w-xl">
        <button
          class="rounded-lg p-1.5 text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary lg:hidden"
          title="Open menu"
          aria-label="Open navigation menu"
          @click="mobileOpen = true"
        >
          <MIcon name="menu" class="text-[22px]" />
        </button>
        <div class="relative min-w-0 flex-1">
          <MIcon name="search" class="absolute top-1/2 left-3 -translate-y-1/2 text-[18px] text-outline" />
          <input
            v-model="searchQuery"
            class="w-full min-w-0 rounded-lg border border-outline-variant bg-surface py-1.5 pr-4 pl-9 font-body-md text-body-md text-on-surface transition-colors placeholder:text-outline focus:border-primary focus:outline-none"
            type="text"
            placeholder="Search shipments, vessels, manifests..."
            @keyup.enter="submitSearch"
          />
        </div>
      </div>

      <div class="flex items-center gap-4">
        <NotificationsNotificationBell />
        <NuxtLink to="/profile" class="hidden rounded-lg p-1.5 text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary sm:inline-flex" title="Help">
          <MIcon name="help_outline" class="text-[20px]" />
        </NuxtLink>
        <div class="hidden h-5 w-px bg-outline-variant lg:block" />
        <span class="hidden text-label-md text-on-surface-variant lg:inline-block">Shipper Enterprise Portal</span>
      </div>
    </header>

    <div class="min-h-screen pt-16 lg:ml-64">
      <slot />

      <footer class="py-4 text-center text-xs text-muted-foreground">
        Sheno B2B Logistics
      </footer>
    </div>
    <NotificationsNotificationToast />
  </div>
</template>