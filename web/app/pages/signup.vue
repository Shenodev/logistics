<template>
  <AuthShell
    title="Create your account"
    description="Join the ShenoFlow network and start moving freight."
  >
    <form @submit="onSubmit" novalidate class="space-y-5">
      <FormField v-slot="{ componentField }" name="name">
        <FormItem>
          <FormLabel>Full name</FormLabel>
          <FormControl>
            <Input
              v-bind="componentField"
              type="text"
              placeholder="Jane Shipper"
              autocomplete="name"
              class="bg-secondary border-border"
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>

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
              placeholder="At least 8 characters"
              autocomplete="new-password"
              class="bg-secondary border-border"
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>

      <FormField v-slot="{ componentField }" name="confirm">
        <FormItem>
          <FormLabel>Confirm password</FormLabel>
          <FormControl>
            <Input
              v-bind="componentField"
              type="password"
              placeholder="Repeat your password"
              autocomplete="new-password"
              class="bg-secondary border-border"
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>

      <FormField v-slot="{ value, handleChange }" name="terms">
        <FormItem class="flex items-start gap-3 space-y-0">
          <FormControl class="mt-0.5 shrink-0">
            <input
              type="checkbox"
              :checked="value"
              class="h-4 w-4 rounded border-border bg-secondary accent-cyan-500"
              @change="handleChange"
            />
          </FormControl>
          <div class="space-y-1">
            <FormLabel class="font-normal leading-5 text-muted-foreground">
              I agree to the
              <button type="button" class="text-cyan-400 underline underline-offset-2">Terms</button>
              and
              <button type="button" class="text-cyan-400 underline underline-offset-2">Privacy Policy</button>
            </FormLabel>
            <FormMessage />
          </div>
        </FormItem>
      </FormField>

      <p
        v-if="auth.loginError"
        class="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive"
      >
        {{ auth.loginError }}
      </p>

      <Button type="submit" class="w-full" :disabled="auth.isPending">
        {{ auth.isPending ? 'Creating account…' : 'Create account' }}
      </Button>
    </form>

    <template #footer>
      <p class="text-center text-sm text-muted-foreground">
        Already have an account?
        <NuxtLink to="/login" class="font-medium text-primary hover:underline">Sign in</NuxtLink>
      </p>
    </template>
  </AuthShell>
</template>

<script setup lang="ts">
import * as z from 'zod'
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'

definePageMeta({ layout: false, middleware: 'guest' })

const auth = useAuthStore()

const signupSchema = toTypedSchema(
  z
    .object({
      name: z
        .string({ required_error: 'Name is required' })
        .min(2, 'Name must be at least 2 characters'),
      email: z
        .string({ required_error: 'Email is required' })
        .email('Enter a valid email address'),
      password: z
        .string({ required_error: 'Password is required' })
        .min(8, 'Password must be at least 8 characters'),
      confirm: z
        .string({ required_error: 'Please confirm your password' }),
      terms: z.boolean({ required_error: 'You must accept the terms to continue' }),
    })
    .refine((data) => data.password === data.confirm, {
      message: 'Passwords do not match',
      path: ['confirm'],
    })
    .refine((data) => data.terms === true, {
      message: 'You must accept the terms to continue',
      path: ['terms'],
    }),
)

const { handleSubmit } = useForm({
  validationSchema: signupSchema,
  initialValues: { name: '', email: '', password: '', confirm: '', terms: false },
})

const onSubmit = handleSubmit(async ({ name, email, password }) => {
  try {
    await auth.signup({ name, email, password })
    await navigateTo('/')
  }
  catch {
    // error surfaced via auth.loginError
  }
})
</script>