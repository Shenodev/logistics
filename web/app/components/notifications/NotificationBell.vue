<script setup lang="ts">
const { items, unread, fetchList, markRead, markAllRead } = useNotifications()
const open = ref(false)

function toggle() {
  open.value = !open.value
  if (open.value) fetchList(20)
}

function onMarkRead(id: number) {
  markRead(id)
}

function onMarkAll() {
  markAllRead()
}

// Close on outside click
function onClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('[data-notif-bell]')) open.value = false
}

onMounted(() => {
  if (typeof window !== 'undefined') window.addEventListener('click', onClickOutside)
})
onUnmounted(() => {
  if (typeof window !== 'undefined') window.removeEventListener('click', onClickOutside)
})
</script>

<template>
  <div data-notif-bell class="relative">
    <button
      class="relative flex min-h-10 min-w-10 items-center justify-center rounded-lg text-on-surface-variant transition-colors hover:bg-surface-container hover:text-primary"
      type="button"
      title="Notifications"
      aria-label="Notifications"
      @click="toggle"
    >
      <MIcon name="notifications" class="text-[22px]" />
      <span
        v-if="unread > 0"
        class="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-destructive px-1 text-[11px] font-bold text-destructive-foreground"
      >
        {{ unread > 99 ? '99+' : unread }}
      </span>
      <span v-if="unread > 0" class="absolute -right-0.5 -top-0.5 h-5 w-5 animate-ping rounded-full bg-destructive/30" />
    </button>

    <div
      v-if="open"
      class="absolute right-0 top-11 z-40 w-80 max-w-[90vw] overflow-hidden rounded-xl border border-outline-variant bg-surface-container shadow-xl"
    >
      <div class="flex items-center justify-between border-b border-outline-variant bg-surface-low px-3 py-2">
        <div class="flex items-center gap-1.5">
          <MIcon name="notifications_active" class="text-[18px] text-primary" />
          <span class="font-heading text-label-md font-semibold text-on-surface">Notifications</span>
          <span v-if="unread > 0" class="rounded-full bg-primary px-1.5 py-0.5 text-[11px] font-bold text-on-primary">{{ unread }} new</span>
        </div>
        <button
          v-if="unread > 0"
          class="rounded px-2 py-1 text-label-sm font-medium text-primary hover:bg-surface-container-high"
          @click="onMarkAll"
        >
          Mark all read
        </button>
      </div>

      <div class="max-h-80 overflow-y-auto">
        <div v-if="items.length === 0" class="p-6 text-center">
          <MIcon name="notifications_none" class="text-[28px] text-outline" />
          <p class="mt-1 text-body-sm font-medium text-on-surface">No notifications</p>
          <p class="text-label-sm text-on-surface-variant">Order transitions will appear here live.</p>
        </div>
        <ul v-else class="divide-y divide-outline-variant/60">
          <li
            v-for="n in items"
            :key="n.id"
            class="flex gap-2 p-3 hover:bg-surface-container-high/50 transition-colors"
            :class="n.is_read ? 'opacity-70' : 'bg-primary/5'"
          >
            <div class="flex size-8 shrink-0 items-center justify-center rounded-full border" :class="n.is_read ? 'border-outline-variant bg-surface-low text-outline' : 'border-primary/30 bg-primary/10 text-primary'">
              <MIcon :name="n.kind === 'order_status' ? 'sync_alt' : n.kind === 'refund' ? 'payments' : 'info'" class="text-[16px]" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1">
                <p class="truncate font-label-md font-semibold text-on-surface">{{ n.title }}</p>
                <span v-if="!n.is_read" class="h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
              </div>
              <p class="mt-0.5 line-clamp-2 text-body-sm leading-snug text-on-surface-variant">{{ n.message }}</p>
              <div class="mt-1 flex items-center gap-2 text-label-sm text-outline">
                <span v-if="n.order_number" class="font-mono text-primary">{{ n.order_number }}</span>
                <span>{{ n.time_ago || '' }}</span>
                <span v-if="n.stage_from" class="hidden sm:inline">{{ n.stage_from }} → {{ n.stage_to }}</span>
              </div>
            </div>
            <button
              v-if="!n.is_read"
              class="self-start rounded p-1 text-outline hover:bg-surface-container hover:text-primary"
              title="Mark read"
              @click="onMarkRead(n.id)"
            >
              <MIcon name="done" class="text-[18px]" />
            </button>
          </li>
        </ul>
      </div>

      <div class="border-t border-outline-variant bg-surface-low px-3 py-2 text-center">
        <span class="text-label-sm text-on-surface-variant">Live via SSE • <span class="text-primary">instant</span> push</span>
      </div>
    </div>
  </div>
</template>
