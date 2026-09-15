<template>
  <main class="flex-1 flex items-center justify-center p-8">
    <Card class="w-full max-w-md bg-card border-border">
      <CardHeader>
        <CardTitle class="text-2xl font-heading">
          Welcome, {{ auth.user?.name }}
        </CardTitle>
        <CardDescription class="flex items-center gap-2">
          {{ auth.user?.email }}
          <Badge :class="auth.isAdmin ? 'bg-primary text-primary-foreground' : 'bg-cyan-900/40 text-cyan-200'">
            {{ auth.isAdmin ? 'Admin' : 'User' }}
          </Badge>
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between rounded-xl border border-border bg-secondary/40 px-4 py-3 text-sm">
          <span class="text-muted-foreground">Session</span>
          <code class="text-cyan-300">{{ host }}</code>
        </div>
        <div class="flex items-center justify-between rounded-xl border border-border bg-secondary/40 px-4 py-3 text-sm">
          <span class="text-muted-foreground">Layout</span>
          <code class="text-cyan-300">{{ layoutName }}</code>
        </div>
      </CardContent>
      <CardFooter class="flex justify-between">
        <span class="text-xs text-muted-foreground">JWT stored in httpOnly cookie</span>
        <Button variant="secondary" class="bg-secondary text-secondary-foreground" :disabled="auth.isPending" @click="handleLogout">
          Sign out
        </Button>
      </CardFooter>
    </Card>
  </main>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const auth = useAuthStore()
const host = useRequestURL().hostname
const layoutName = computed(() => (auth.isAdmin ? 'admin' : 'user'))

async function handleLogout() {
  await auth.logout()
  await navigateTo('/login')
}
</script>