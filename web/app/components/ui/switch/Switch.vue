<script setup lang="ts">
import type { SwitchRootProps } from "reka-ui"
import type { HTMLAttributes } from "vue"
import { reactiveOmit } from "@vueuse/core"
import { SwitchRoot, SwitchThumb, useForwardProps } from "reka-ui"
import { cn } from "@/lib/utils"

interface Props extends SwitchRootProps {
  class?: HTMLAttributes["class"]
}

const props = defineProps<Props>()

const delegatedProps = reactiveOmit(props, "class")
const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <SwitchRoot
    data-slot="switch"
    :class="cn(
      'peer data-[state=checked]:bg-primary data-[state=unchecked]:bg-surface-container-highest focus-visible:ring-ring/50 focus-visible:ring-3 inline-flex h-5 w-9 shrink-0 items-center rounded-full border border-transparent shadow-xs transition-all outline-none disabled:cursor-not-allowed disabled:opacity-50',
      props.class,
    )"
    v-bind="forwardedProps"
  >
    <SwitchThumb
      data-slot="switch-thumb"
      :class="cn(
        'bg-background dark:data-[state=unchecked]:bg-on-surface-variant dark:data-[state=checked]:bg-primary-foreground pointer-events-none block size-4 rounded-full ring-0 transition-transform data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0.5',
      )"
    />
  </SwitchRoot>
</template>