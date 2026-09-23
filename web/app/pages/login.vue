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

      <!-- Demo auto-fill — portal-aware, one click to try -->
      <div class="space-y-3 pt-1">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <span class="w-full border-t border-dashed border-border/60" />
          </div>
          <div class="relative flex justify-center text-[11px]">
            <span class="bg-card px-2.5 text-muted-foreground tracking-widest uppercase">Try the demo</span>
          </div>
        </div>
        <button
          type="button"
          class="group flex w-full items-center gap-3 rounded-xl border border-dashed border-border/70 bg-muted/20 px-4 py-3 text-left transition hover:border-solid hover:bg-muted/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          :aria-label="demoCreds.label"
          @click="fillDemo"
        >
          <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border bg-background text-primary">
            <MIcon :name="demoCreds.icon" class="text-[18px]" />
          </span>
          <span class="min-w-0 flex-1">
            <span class="block text-sm font-medium leading-none">{{ demoCreds.label }}</span>
            <span class="block truncate text-xs text-muted-foreground">{{ demoCreds.sub }}</span>
          </span>
          <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground transition group-hover:translate-x-0.5">
            <MIcon name="arrow_forward" class="text-[16px]" />
          </span>
        </button>
      </div>

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
        devHint: 'admin@shenodev.tech / admin123',
        showSignup: false,
        footerNote: 'Admin access is provisioned by Sheno fleet operations.',
      }
    case 'delivery':
      return {
        title: 'Driver sign in',
        description: 'Driver access to the Sheno delivery network',
        seoTitle: 'Driver sign in',
        devHint: 'delivery@shenodev.tech / delivery123',
        showSignup: true,
        footerNote: '',
      }
    default:
      return {
        title: 'Sign in to ShenoFlow',
        description: 'Customer portal access',
        seoTitle: 'Sign in',
        devHint: 'user@shenodev.tech / user123',
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

const { handleSubmit, setFieldValue } = useForm({
  validationSchema: loginSchema,
  initialValues: { email: '', password: '' },
})

const demoCreds = computed(() => {
  if (portal === 'admin') return { email: 'admin@shenodev.tech', password: 'admin123', label: 'Login as Demo Admin', sub: 'admin@shenodev.tech · Command Center', icon: 'shield' }
  if (portal === 'delivery') return { email: 'delivery@shenodev.tech', password: 'delivery123', label: 'Login as Demo Driver', sub: 'delivery@shenodev.tech · Delivery PWA', icon: 'local_shipping' }
  return { email: 'user@shenodev.tech', password: 'user123', label: 'Login as Demo User', sub: 'user@shenodev.tech · Customer Portal', icon: 'inventory_2' }
})

function fillDemo() {
  setFieldValue('email', demoCreds.value.email)
  setFieldValue('password', demoCreds.value.password)
}

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