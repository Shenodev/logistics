<template>
  <div class="min-h-screen bg-background text-foreground flex flex-col">
    <header class="border-b border-border bg-card/50 backdrop-blur">
      <div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <AppBrand suffix="Admin" />
        <Badge class="bg-primary text-primary-foreground">Command Center</Badge>
      </div>
    </header>

    <slot />

    <footer class="mt-auto border-t border-border py-4 text-center text-xs text-muted-foreground">
      admin.logistics.shenodev.tech — Dispatcher / Admin
    </footer>
  </div>
</template>