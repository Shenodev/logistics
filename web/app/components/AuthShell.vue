<script setup lang="ts">
interface Props {
  title: string
  description?: string
  showOtp?: boolean
}
withDefaults(defineProps<Props>(), {})
</script>

<template>
  <div class="grid min-h-[100dvh] bg-background text-foreground lg:grid-cols-[1.05fr_1fr]">
    <section class="relative hidden overflow-hidden border-r border-border lg:flex lg:flex-col">
      <div
        class="pointer-events-none absolute inset-0 opacity-[0.05]"
        style="background-image:
          linear-gradient(to right, rgba(148, 163, 184, 0.6) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(148, 163, 184, 0.6) 1px, transparent 1px);
          background-size: 44px 44px;"
      />
      <div class="pointer-events-none absolute -left-32 bottom-10 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl" />

      <div class="relative z-10 flex flex-1 flex-col">
        <div class="p-10">
          <AppBrand />
        </div>

        <div class="flex flex-1 items-center px-10">
          <div class="max-w-lg py-6">
            <h1 class="font-heading text-4xl font-bold leading-tight tracking-tight text-foreground">
              Move freight like clockwork.
            </h1>
            <p class="mt-5 max-w-md text-muted-foreground">
              Fleet, dispatch, and tracking for the Sheno B2B logistics network. One portal for every consignment, from pickup to proof of delivery.
            </p>
          </div>
        </div>
      </div>

      <footer class="relative z-10 border-t border-border/60 p-10 text-xs text-muted-foreground">
        Sheno B2B Logistics
      </footer>
    </section>

    <main class="flex items-center justify-center p-6 sm:p-10">
      <div class="w-full max-w-sm">
        <div class="mb-8 lg:hidden">
          <AppBrand />
        </div>
        <Card class="border-border bg-card/60 backdrop-blur">
          <CardHeader>
            <CardTitle class="font-heading text-2xl font-bold tracking-tight">
              {{ title }}
            </CardTitle>
            <CardDescription v-if="description">
              {{ description }}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <slot />
          </CardContent>
          <CardFooter v-if="$slots.footer" class="flex flex-col items-stretch gap-4">
            <slot name="footer" />
          </CardFooter>
        </Card>
      </div>
    </main>
  </div>
</template>