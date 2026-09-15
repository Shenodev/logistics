<template>
  <AuthShell
    title="Sign in to ShenoFlow"
    :description="isAdminHost ? 'Dispatcher / Admin access' : 'Customer portal access'"
  >
    <form @submit="onSubmit" novalidate class="space-y-5">
      <FormField v-slot="{ componentField }" name="email">
        <FormItem>
          <FormLabel>Email</FormLabel>
          <FormControl>
            <Input
              v-bind="componentField"
              type="email"
              placeholder="you@sheno.dev"
              autocomplete="email"
              class="bg-secondary border-border"
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>

      <FormField v-slot="{ componentField }" name="password">
        <FormItem>
          <FormLabel>Password</FormLabel>
          <FormControl>
            <Input
              v-bind="componentField"
              type="password"
              placeholder="••••••••"
              autocomplete="current-password"
              class="bg-secondary border-border"
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>

      <p
        v-if="auth.loginError"
        class="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive"
      >
        {{ auth.loginError }}
      </p>

      <Button type="submit" class="w-full" :disabled="auth.isPending">
        {{ auth.isPending ? 'Signing in…' : 'Sign in' }}
      </Button>
      <p class="text-center text-xs text-muted-foreground">
        Dev demo:
        <code class="text-cyan-300">{{ devHint }}</code>
      </p>
    </form>

    <template #footer>
      <div class="flex items-center gap-3">
        <Separator class="flex-1 bg-border" />
        <span class="text-xs text-muted-foreground">or</span>
        <Separator class="flex-1 bg-border" />
      </div>
      <Button variant="outline" class="w-full" as-child>
        <NuxtLink to="/signup">Create an account</NuxtLink>
      </Button>
    </template>
  </AuthShell>
</template>

<script setup lang="ts">
import * as z from 'zod'
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'

definePageMeta({ layout: false, middleware: 'guest' })

const route = useRoute()
const isAdminHost = useAppRole() === 'admin'

useSeoMeta({
  title: `${isAdminHost ? 'Dispatcher sign in' : 'Sign in'}`,
  description: 'Sign in to the ShenoFlow logistics portal to manage shipments, fleet, and dispatch.',
})
const auth = useAuthStore()

const loginSchema = toTypedSchema(
  z.object({
    email: z
      .string({ required_error: 'Email is required' })
      .email('Enter a valid email address'),
    password: z
      .string({ required_error: 'Password is required' })
      .min(1, 'Password is required'),
  }),
)

const { handleSubmit } = useForm({
  validationSchema: loginSchema,
  initialValues: { email: '', password: '' },
})

const devHint = isAdminHost ? 'admin@sheno.dev / admin123' : 'user@sheno.dev / user123'

const onSubmit = handleSubmit(async ({ email, password }) => {
  try {
    await auth.login({ email, password })
    await navigateTo(safeRedirectTarget(route.query.redirect))
  }
  catch {
    // error surfaced via auth.loginError
  }
})
</script>