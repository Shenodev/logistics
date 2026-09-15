<script setup lang="ts">
import { timezones } from '~~/app/data/profile'

definePageMeta({ layout: 'user', middleware: 'auth' })

useSeoMeta({
  title: 'Settings',
  description: 'Tune ShenoFlow portal defaults, interface density, units, currency, and data exports.',
})

const settings = ref({
  preferredMode: 'Ocean FCL',
  currency: 'USD (US Dollar)',
  unitSystem: 'Metric',
  defaultOrigin: 'Newark, NJ, United States',
  defaultDestination: 'Rotterdam, Netherlands',
  dateFormat: 'Nov 12, 2024',
  language: 'English (US)',
  timezone: timezones[0],
  compactDensity: false,
})

const modes = ['Ocean FCL', 'Ocean LCL', 'Air Express', 'Road Truckload', 'Intermodal']
const currencies = ['USD (US Dollar)', 'EUR (Euro)', 'SGD (Singapore Dollar)']
const unitSystems = ['Metric', 'Imperial']
const dateFormats = ['Nov 12, 2024', '2024-11-12', '12 Nov 2024']
const languages = ['English (US)', 'Español', '中文 (简体)']
const origins = ['Newark, NJ, United States', 'Rotterdam, Netherlands', 'Singapore, Singapore', 'Bremerhaven, Germany']
const destinations = ['Rotterdam, Netherlands', 'Singapore, Singapore', 'Newark, NJ, United States', 'Hamburg, Germany']

const saved = ref(false)

function persist() {
  saved.value = true
  setTimeout(() => (saved.value = false), 4000)
}
</script>

<template>
  <main class="bg-background">
    <div class="mx-auto max-w-[1600px] space-y-6 p-6">
      <!-- Header -->
      <section class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div class="flex items-center gap-2 text-body-sm text-on-surface-variant">
            <span class="font-label-md uppercase tracking-wider text-on-surface-variant">Global Freight Portal</span>
            <span class="text-outline-variant">/</span>
            <span class="text-primary font-medium">Settings</span>
          </div>
          <h1 class="mt-1 font-heading text-headline-lg font-bold tracking-tight text-on-surface">Portal Settings</h1>
          <p class="text-body-sm text-on-surface-variant">Tune defaults that apply across overview, shipments, and billing</p>
        </div>
        <Button class="gap-1.5 self-start rounded-lg bg-primary px-4 py-2 font-label-md font-bold text-on-surface hover:bg-primary-container sm:self-auto" @click="persist">
          <MIcon name="settings_suggest" class="text-[18px]" />
          Save Settings
        </Button>
      </section>

      <p v-if="saved" class="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-2.5 text-body-sm text-emerald-400">
        Settings saved and applied across the portal for all users in this organization.
      </p>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div class="space-y-6 lg:col-span-8">
          <!-- Operational defaults -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2 border-b border-outline-variant pb-3">
              <MIcon name="tune" class="text-[22px] text-primary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Operational Defaults</h2>
            </div>

            <form class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2" @submit.prevent="persist">
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Preferred shipping mode</span>
                <select v-model="settings.preferredMode" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option v-for="mode in modes" :key="mode" :value="mode">{{ mode }}</option>
                </select>
              </label>
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Default currency</span>
                <select v-model="settings.currency" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option v-for="currency in currencies" :key="currency" :value="currency">{{ currency }}</option>
                </select>
              </label>
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Unit system</span>
                <select v-model="settings.unitSystem" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option v-for="system in unitSystems" :key="system" :value="system">{{ system }}</option>
                </select>
              </label>
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Default origin</span>
                <select v-model="settings.defaultOrigin" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option v-for="origin in origins" :key="origin" :value="origin">{{ origin }}</option>
                </select>
              </label>
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Default destination</span>
                <select v-model="settings.defaultDestination" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option v-for="destination in destinations" :key="destination" :value="destination">{{ destination }}</option>
                </select>
              </label>
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Date format</span>
                <select v-model="settings.dateFormat" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option v-for="format in dateFormats" :key="format" :value="format">{{ format }}</option>
                </select>
              </label>
            </form>
          </section>

          <!-- Interface -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2 border-b border-outline-variant pb-3">
              <MIcon name="view_cozy" class="text-[22px] text-secondary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Interface</h2>
            </div>

            <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Language</span>
                <select v-model="settings.language" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option v-for="language in languages" :key="language" :value="language">{{ language }}</option>
                </select>
              </label>
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Time zone</span>
                <select v-model="settings.timezone" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option v-for="tz in timezones" :key="tz" :value="tz">{{ tz }}</option>
                </select>
              </label>
            </div>

            <div class="mt-4 flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-3">
              <div>
                <p class="font-label-md font-semibold text-on-surface">Compact density</p>
                <p class="mt-0.5 text-body-sm text-on-surface-variant">Tighter spacing for the shipments list and invoice table</p>
              </div>
              <Switch v-model:checked="settings.compactDensity" aria-label="Toggle compact density" />
            </div>

            <p class="mt-4 text-body-sm text-on-surface-variant">
              Theme is locked to the ShenoFlow dark reference for enterprise consistency. Request light mode via
              <NuxtLink to="/support" class="text-primary underline">Support</NuxtLink>.
            </p>
          </section>
        </div>

        <div class="space-y-6 lg:col-span-4">
          <!-- Data & exports -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2">
              <MIcon name="file_download" class="text-[22px] text-tertiary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Data &amp; Exports</h2>
            </div>
            <p class="mt-2 text-body-sm leading-relaxed text-on-surface-variant">
              Statements, manifest dumps, and customs summaries follow the formats below.
            </p>
            <ul class="mt-4 space-y-2">
              <li class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5 text-label-md">
                <span class="text-on-surface">Billing statement</span>
                <span class="text-label-sm text-on-surface-variant">CSV</span>
              </li>
              <li class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5 text-label-md">
                <span class="text-on-surface">Manifest export</span>
                <span class="text-label-sm text-on-surface-variant">EDIFACT</span>
              </li>
              <li class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5 text-label-md">
                <span class="text-on-surface">Customs packets</span>
                <span class="text-label-sm text-on-surface-variant">PDF</span>
              </li>
            </ul>
            <a class="mt-4 inline-flex items-center gap-1.5 text-label-md font-semibold text-primary transition-colors hover:text-on-surface" href="/billing">
              <MIcon name="receipt_long" class="text-[18px]" />
              Download statement from Billing
            </a>
          </section>

          <!-- Organization -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2">
              <MIcon name="business" class="text-[22px] text-primary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Organization Scope</h2>
            </div>
            <p class="mt-2 text-body-sm leading-relaxed text-on-surface-variant">
              Defaults apply portal-wide for <strong class="text-on-surface">Shenodev Logistics</strong>. Notifications,
              security, and billing addresses are managed on your profile.
            </p>
            <div class="mt-4 space-y-2">
              <NuxtLink class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5 transition-colors hover:border-primary/50" to="/profile">
                <span class="flex items-center gap-2 text-label-md text-on-surface">
                  <MIcon name="account_circle" class="text-[18px] text-primary" />
                  Profile &amp; notifications
                </span>
                <MIcon name="arrow_outward" class="text-[16px] text-on-surface-variant" />
              </NuxtLink>
              <NuxtLink class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5 transition-colors hover:border-primary/50" to="/support">
                <span class="flex items-center gap-2 text-label-md text-on-surface">
                  <MIcon name="help" class="text-[18px] text-primary" />
                  Help &amp; escalation
                </span>
                <MIcon name="arrow_outward" class="text-[16px] text-on-surface-variant" />
              </NuxtLink>
            </div>
          </section>
        </div>
      </div>
    </div>
  </main>
</template>