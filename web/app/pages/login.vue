<template>
  <main class="flex-1 flex items-center justify-center p-8">
    <Card class="w-full max-w-sm bg-card border-border">
      <CardHeader>
        <CardTitle class="text-2xl font-heading">Sign in to ShenoFlow</CardTitle>
        <CardDescription>
          {{ isAdminHost ? 'Dispatcher / Admin access' : 'Customer portal access' }}
        </CardDescription>
      </CardHeader>
      <form @submit.prevent="handleSubmit">
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label for="email" class="text-sm font-medium">Email</Label>
            <Input
              id="email"
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="you@sheno.dev"
              class="bg-secondary border-border"
              required
            />
          </div>
          <div class="space-y-2">
            <Label for="password" class="text-sm font-medium">Password</Label>
            <Input
              id="password"
              v-model="password"
              type="password"
              autocomplete="current-password"
              placeholder="••••••••"
              class="bg-secondary border-border"
              required
            />
          </div>
          <p v-if="auth.loginError" class="text-sm text-destructive">{{ auth.loginError }}</p>
        </CardContent>
        <CardFooter class="flex flex-col items-stretch gap-2">
          <Button type="submit" class="bg-primary text-primary-foreground" :disabled="auth.isPending">
            {{ auth.isPending ? 'Signing in...' : 'Sign in' }}
          </Button>
          <p class="text-center text-xs text-muted-foreground">
            Dev demo: use <code class="text-cyan-300">{{ devHint }}</code>
          </p>
        </CardFooter>
      </form>
    </Card>
  </main>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'guest' })

const route = useRoute()
const isAdminHost = useAppRole() === 'admin'

const email = ref('')
const password = ref('')
const auth = useAuthStore()

const devHint = isAdminHost ? 'admin@sheno.dev / admin123' : 'user@sheno.dev / user123'

async function handleSubmit() {
  try {
    await auth.login({ email: email.value, password: password.value })
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await navigateTo(redirect)
  }
  catch {
    // error surfaced via auth.loginError
  }
}
</script>