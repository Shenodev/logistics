<script setup lang="ts">
const auth = useAuthStore()
const router = useRouter()

async function logout() {
  await auth.logout()
  await router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-background text-foreground flex flex-col">
    <header class="sticky top-0 z-20 border-b border-border bg-card/50 backdrop-blur">
      <div class="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4">
        <AppBrand suffix="Admin" />
        <nav class="hidden md:flex items-center gap-1">
          <NuxtLink to="/admin" class="rounded-lg px-3 py-1.5 text-label-md font-medium transition-colors" :class="$route.path==='/admin' ? 'bg-surface-container text-primary border border-outline-variant' : 'text-on-surface-variant hover:text-on-surface'">Command Center</NuxtLink>
          <NuxtLink to="/admin/route-planning" class="rounded-lg px-3 py-1.5 text-label-md font-medium transition-colors" :class="$route.path.startsWith('/admin/route-planning') ? 'bg-surface-container text-primary border border-outline-variant' : 'text-on-surface-variant hover:text-on-surface'">Route Planning</NuxtLink>
        </nav>
        <div class="flex items-center gap-3">
          <Badge class="bg-primary text-primary-foreground">Command Center</Badge>
          <div class="hidden items-center gap-2 sm:flex">
            <div class="flex size-8 items-center justify-center rounded-full border border-outline-variant bg-surface-container-highest text-label-sm font-bold text-primary">
              {{ auth.user?.name?.charAt(0)?.toUpperCase() || 'A' }}
            </div>
            <span class="max-w-[140px] truncate text-label-md text-on-surface-variant">
              {{ auth.user?.email }}
            </span>
          </div>
          <button
            class="flex min-h-10 min-w-10 items-center justify-center rounded-lg text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary"
            type="button"
            title="Sign out"
            aria-label="Sign out"
            @click="logout"
          >
            <MIcon name="logout" class="text-[20px]" />
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto w-full max-w-6xl flex-1 px-4 py-6">
      <slot />
    </main>

    <footer class="mt-auto border-t border-border py-4 text-center text-xs text-muted-foreground">
      Dispatcher / Admin Console
    </footer>
  </div>
</template>