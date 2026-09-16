<script setup lang="ts">
import { canCancelOrder } from '~~/app/data/shipments'
import type { Shipment } from '~~/app/data/shipments'

interface Props {
  shipment: Shipment
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const emit = defineEmits<{
  cancel: []
}>()

// Vue conditional rendering gate: Stage 1 only ("Order Received" / "استلام الطلب")
const isCancellable = computed(() => canCancelOrder(props.shipment))
</script>

<template>
  <!-- CRITICAL: Cancel button only visible when status is exactly Order Received (Stage 1) -->
  <button
    v-if="isCancellable"
    type="button"
    class="inline-flex items-center gap-1.5 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2 text-label-md font-semibold text-destructive transition-colors hover:bg-destructive hover:text-destructive-foreground active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none"
    :disabled="loading"
    @click="emit('cancel')"
  >
    <MIcon name="cancel" class="text-[18px]" />
    <span>{{ loading ? 'Cancelling…' : 'Cancel Order' }}</span>
  </button>
</template>
