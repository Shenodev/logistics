<template>
  <AuthShell :title="portalMeta.title" :description="portalMeta.description">
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
      <p v-if="portalMeta.devHint" class="text-center text-xs text-muted-foreground">
        Dev demo:
        <code class="text-cyan-300">{{ portalMeta.devHint }}</code>
      </p>
    </form>

    <template #footer>
      <template v-if="portalMeta.showSignup">
        <div class="flex items-center gap-3">
          <Separator class="flex-1 bg-border" />
          <span class="text-xs text-muted-foreground">or</span>
          <Separator class="flex-1 bg-border" />
        </div>
        <Button variant="outline" class="w-full" as-child>
          <NuxtLink to="/signup">New driver? Create an account</NuxtLink>
        </Button>
      </template>
      <p v-else-if="portalMeta.footerNote" class="text-center text-xs text-muted-foreground">
        {{ portalMeta.footerNote }}
      </p>
    </template>
  </AuthShell>
</template>

<script setup lang="ts">
import * as z from 'zod'
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'

definePageMeta({ layout: false, middleware: 'guest' })

const route = useRoute()
const auth = useAuthStore()
const portal = useAppRole()

const portalMeta = computed(() => {
  switch (portal) {
    case 'admin':
      return {
        title: 'Sign in to Command Center',
        description: 'Dispatcher / Admin access',
        seoTitle: 'Dispatcher sign in',
        devHint: 'admin@sheno.dev / admin123',
        showSignup: false,
        footerNote: 'Admin access is provisioned by Sheno fleet operations.',
      }
    case 'delivery':
      return {
        title: 'Driver sign in',
        description: 'Driver access to the Sheno delivery network',
        seoTitle: 'Driver sign in',
        devHint: '',
        showSignup: true,
        footerNote: '',
      }
    default:
      return {
        title: 'Sign in to ShenoFlow',
        description: 'Customer portal access',
        seoTitle: 'Sign in',
        devHint: 'user@sheno.dev / user123',
        showSignup: false,
        footerNote: 'Portal access is provisioned by your shipper organization.',
      }
  }
})

const destination = computed(() => {
  const redirect = typeof route.query.redirect === 'string' && isSafeRedirect(route.query.redirect)
    ? route.query.redirect
    : ''
  return redirect || (portal === 'admin' ? '/admin' : '/')
})

useSeoMeta({
  title: computed(() => portalMeta.value.seoTitle),
  description: 'Sign in to the ShenoFlow logistics network.',
})

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

const onSubmit = handleSubmit(async ({ email, password }) => {
  try {
    await auth.login({ email, password })
    await navigateTo(destination.value)
  }
  catch {
    // error surfaced via auth.loginError
  }
})
</script>