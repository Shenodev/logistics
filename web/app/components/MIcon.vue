<script setup lang="ts">
interface Props {
  name: string
  filled?: boolean
}

withDefaults(defineProps<Props>(), { filled: false })
</script>

<template>
  <span
    class="material-symbols-outlined"
    :class="filled && 'filled'"
    aria-hidden="true"
  >{{ name }}</span>
</template>