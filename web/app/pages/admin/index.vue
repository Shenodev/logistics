<template>
  <main class="flex-1 flex items-center justify-center p-8">
    <Card class="w-full max-w-md bg-card border-border">
      <CardHeader>
        <CardTitle class="text-2xl font-heading">
          Admin console
        </CardTitle>
        <CardDescription class="flex items-center gap-2">
          {{ auth.user?.email }}
          <Badge class="bg-primary text-primary-foreground">Admin</Badge>
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center justify-between rounded-xl border border-border bg-secondary/40 px-4 py-3 text-sm">
          <span class="text-muted-foreground">Host</span>
          <code class="text-cyan-300">{{ host }}</code>
        </div>
        <div class="flex items-center justify-between rounded-xl border border-border bg-secondary/40 px-4 py-3 text-sm">
          <span class="text-muted-foreground">Route guard</span>
          <code class="text-cyan-300">middleware: admin</code>
        </div>
        <div class="flex items-center justify-between rounded-xl border border-border bg-secondary/40 px-4 py-3 text-sm">
          <span class="text-muted-foreground">Role</span>
          <code class="text-cyan-300">{{ auth.role }}</code>
        </div>
      </CardContent>
      <CardFooter class="flex justify-between">
        <span class="text-xs text-muted-foreground">Admin-only route — requires isAdmin</span>
        <Button variant="secondary" class="bg-secondary text-secondary-foreground" :disabled="auth.isPending" @click="handleLogout">
          Sign out
        </Button>
      </CardFooter>
    </Card>
  </main>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'admin' })

useSeoMeta({
  title: 'Admin console',
  description: 'Dispatcher and admin console for the ShenoFlow logistics network.',
})

const auth = useAuthStore()
const host = useRequestURL().hostname

async function handleLogout() {
  await auth.logout()
  await navigateTo('/login')
}
</script>