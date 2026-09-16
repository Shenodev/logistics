<script setup lang="ts">
interface Props {
  label: string
  badge: string
  badgeTone?: 'primary' | 'tertiary'
  badgeIcon?: string
  value: string
  valueCaption: string
  footnote: string
  footerLabel: string
  footerValue: string
  footerKind?: 'bar' | 'stepper' | 'text'
  barPct?: number
}

withDefaults(defineProps<Props>(), {
  badgeTone: 'primary',
  footerKind: 'text',
  barPct: 0,
})
</script>

<template>
  <div class="relative flex flex-col justify-between overflow-hidden rounded-xl border border-outline-variant bg-surface-container p-4">
    <div>
      <div class="mb-1 flex items-center justify-between">
        <span class="text-label-sm uppercase tracking-wider text-on-surface-variant">{{ label }}</span>
        <span
          class="flex items-center gap-0.5 rounded border px-1.5 py-0.5 text-label-sm font-semibold"
          :class="badgeTone === 'primary'
            ? 'border-primary/20 bg-primary/10 text-primary'
            : 'border-tertiary-container/30 bg-tertiary-container/20 text-tertiary'"
        >
          <MIcon v-if="badgeIcon" :name="badgeIcon" class="text-[12px]" />
          {{ badge }}
        </span>
      </div>
      <div class="mb-1 flex items-baseline gap-1">
        <span class="font-heading font-telemetry-numeric text-3xl leading-tight font-bold text-on-surface">{{ value }}</span>
        <span class="text-body-sm font-semibold" :class="badgeTone === 'tertiary' ? 'text-tertiary' : 'text-primary'">
          {{ valueCaption }}
        </span>
      </div>
      <p class="text-body-sm text-on-surface-variant">{{ footnote }}</p>
    </div>

    <div class="mt-4 border-t border-outline-variant/60 pt-4">
      <template v-if="footerKind === 'bar'">
        <div class="mb-1 flex items-center justify-between font-label-sm text-on-surface-variant">
          <span>{{ footerLabel }}</span>
          <span class="font-telemetry-numeric text-on-surface">{{ footerValue }}</span>
        </div>
        <div class="h-1.5 w-full overflow-hidden rounded-full bg-surface-container-high">
          <div class="h-full rounded-full bg-primary" :style="{ width: `${barPct}%` }" />
        </div>
      </template>
      <template v-else-if="footerKind === 'stepper'">
        <div class="flex items-center justify-between font-label-sm">
          <span class="text-on-surface-variant">{{ footerLabel }}</span>
          <span class="font-telemetry-numeric text-tertiary">{{ footerValue }}</span>
        </div>
        <div class="mt-1.5 grid grid-cols-6 gap-1">
          <div v-for="n in 4" :key="`done-${n}`" class="h-1.5 rounded bg-primary" />
          <div v-for="n in 2" :key="`hold-${n}`" class="h-1.5 rounded bg-tertiary" />
        </div>
      </template>
      <template v-else>
        <div class="flex items-center justify-between font-label-sm">
          <span class="text-on-surface-variant">{{ footerLabel }}</span>
          <span class="font-telemetry-numeric font-medium text-on-surface">{{ footerValue }}</span>
        </div>
      </template>
    </div>
  </div>
</template>