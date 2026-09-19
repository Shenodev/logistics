<script setup lang="ts">
import { activeSessions as seedSessions, billingAddresses, notificationPrefs, timezones, type BillingAddress, type NotificationPref } from '~~/app/data/profile'

definePageMeta({ layout: 'user', middleware: 'auth' })

useSeoMeta({
  title: 'Profile & Settings',
  description: 'Manage your ShenoFlow account, notification preferences, security, and shipping addresses.',
})

const auth = useAuthStore()

const displayName = computed(() => auth.user?.name || 'Shipper')
const displayEmail = computed(() => auth.user?.email || 'user@sheno.dev')
const initials = computed(() =>
  displayName.value.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase(),
)

// ---- Persistence helpers ----
const LS = {
  profile: 'shenoflow:profile',
  prefs: 'shenoflow:prefs',
  addresses: 'shenoflow:addresses',
  channel: 'shenoflow:channel',
  twoFactor: 'shenoflow:twoFactor',
  sessions: 'shenoflow:sessions',
} as const

function safeParse<T>(raw: string | null, fallback: T): T {
  if (!raw) return fallback
  try { return JSON.parse(raw) as T } catch { return fallback }
}

// ---- Profile form — now working with localStorage ----
const saveProfile = ref({ organization: 'Shenodev Logistics', phone: '+1 (212) 555-0148', timezone: timezones[0] })
const profileSaved = ref(false)
const profileError = ref<string | null>(null)
const profileSaving = ref(false)

onMounted(() => {
  if (!import.meta.client) return
  const stored = safeParse<{ organization?: string; phone?: string; timezone?: string }>(localStorage.getItem(LS.profile), null)
  if (stored) {
    if (stored.organization) saveProfile.value.organization = stored.organization
    if (stored.phone) saveProfile.value.phone = stored.phone
    if (stored.timezone && timezones.includes(stored.timezone)) saveProfile.value.timezone = stored.timezone
  }
})

function persistProfile() {
  profileError.value = null
  if (!saveProfile.value.organization.trim()) {
    profileError.value = 'Organization is required.'
    return
  }
  if (!saveProfile.value.phone.trim() || !/^\+?[0-9\s().-]{7,25}$/.test(saveProfile.value.phone.trim())) {
    profileError.value = 'Enter a valid phone number.'
    return
  }
  profileSaving.value = true
  try {
    if (import.meta.client) {
      localStorage.setItem(LS.profile, JSON.stringify(saveProfile.value))
    }
    profileSaved.value = true
    setTimeout(() => (profileSaved.value = false), 3500)
  } catch {
    profileError.value = 'Failed to save profile. Try again.'
  } finally {
    profileSaving.value = false
  }
}

// ---- Addresses — persisted ----
const addresses = ref<BillingAddress[]>([...billingAddresses])
const addOpen = ref(false)
const addSuccess = ref<string | null>(null)
const addressError = ref<string | null>(null)

onMounted(() => {
  if (!import.meta.client) return
  const stored = safeParse<BillingAddress[]>(localStorage.getItem(LS.addresses), null)
  if (stored && Array.isArray(stored) && stored.length) addresses.value = stored
})

watch(addresses, (val) => {
  if (!import.meta.client) return
  try { localStorage.setItem(LS.addresses, JSON.stringify(val)) } catch {}
}, { deep: true })

const newAddress = ref({
  label: '',
  line1: '',
  city: '',
  zip: '',
  country: '',
})

function hasAddressInput() {
  return newAddress.value.label.trim() && newAddress.value.line1.trim() && newAddress.value.city.trim()
}

function addAddress() {
  addressError.value = null
  if (!hasAddressInput()) {
    addressError.value = 'Label, street and city are required.'
    return
  }
  const id = `addr_${Date.now()}`
  const makingDefault = addresses.value.length === 0
  addresses.value.unshift({
    id,
    label: newAddress.value.label.trim(),
    line1: newAddress.value.line1.trim(),
    line2: '',
    city: newAddress.value.city.trim(),
    zip: newAddress.value.zip.trim(),
    country: newAddress.value.country.trim() || 'United States',
    isDefault: makingDefault,
  })
  if (makingDefault) {
    addresses.value = addresses.value.map((a) => ({ ...a, isDefault: a.id === id }))
  }
  newAddress.value = { label: '', line1: '', city: '', zip: '', country: '' }
  addOpen.value = false
  addSuccess.value = `Address “${addresses.value[0].label}” saved.`
  setTimeout(() => (addSuccess.value = null), 4000)
}

function setDefault(id: string) {
  addresses.value = addresses.value.map((a) => ({ ...a, isDefault: a.id === id }))
}

function removeAddress(id: string) {
  const removing = addresses.value.find((a) => a.id === id)
  addresses.value = addresses.value.filter((a) => a.id !== id)
  if (removing?.isDefault && addresses.value[0]) {
    setDefault(addresses.value[0].id)
  }
}

// ---- Notification prefs — persisted ----
const prefs = ref<NotificationPref[]>([...notificationPrefs])
const channel = ref<'email' | 'sms'>('email')

onMounted(() => {
  if (!import.meta.client) return
  const storedPrefs = safeParse<NotificationPref[]>(localStorage.getItem(LS.prefs), null)
  if (storedPrefs && Array.isArray(storedPrefs) && storedPrefs.length) prefs.value = storedPrefs
  const storedChannel = localStorage.getItem(LS.channel) as 'email' | 'sms' | null
  if (storedChannel === 'email' || storedChannel === 'sms') channel.value = storedChannel
})

watch(prefs, (val) => {
  if (!import.meta.client) return
  try { localStorage.setItem(LS.prefs, JSON.stringify(val)) } catch {}
}, { deep: true })

watch(channel, (val) => {
  if (!import.meta.client) return
  try { localStorage.setItem(LS.channel, val) } catch {}
})

// ---- Security — persisted ----
const twoFactor = ref(true)
const sessions = ref([...seedSessions])
const revokedMsg = ref<string | null>(null)
const pwdMsg = ref<string | null>(null)

onMounted(() => {
  if (!import.meta.client) return
  const stored2fa = localStorage.getItem(LS.twoFactor)
  if (stored2fa !== null) twoFactor.value = stored2fa === 'true'
  const storedSessions = safeParse<typeof seedSessions>(localStorage.getItem(LS.sessions), null)
  if (storedSessions && Array.isArray(storedSessions)) sessions.value = storedSessions
})

watch(twoFactor, (val) => {
  if (!import.meta.client) return
  try { localStorage.setItem(LS.twoFactor, String(val)) } catch {}
})

watch(sessions, (val) => {
  if (!import.meta.client) return
  try { localStorage.setItem(LS.sessions, JSON.stringify(val)) } catch {}
}, { deep: true })

function revokeSession(device: string) {
  sessions.value = sessions.value.filter((s) => s.device !== device)
  revokedMsg.value = `Revoked ${device}.`
  setTimeout(() => (revokedMsg.value = null), 3000)
}

function changePassword() {
  pwdMsg.value = 'Password change is handled by your SSO admin. Request a reset link via support@sheno.dev.'
  setTimeout(() => (pwdMsg.value = null), 4000)
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
            <span class="text-primary font-medium">Profile</span>
          </div>
          <h1 class="mt-1 font-heading text-headline-lg font-bold tracking-tight text-on-surface">Profile &amp; Settings</h1>
          <p class="text-body-sm text-on-surface-variant">Account, notifications, security, and shipping addresses — all saved locally and working</p>
        </div>
        <div class="flex items-center gap-2 rounded-lg border border-outline-variant bg-surface-container px-3 py-2">
          <MIcon name="verified_user" class="text-[20px] text-primary" />
          <span class="text-label-md font-medium text-on-surface">Enterprise tier · Annual contract</span>
        </div>
      </section>

      <p v-if="addSuccess" class="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-2.5 text-body-sm text-emerald-400">
        {{ addSuccess }}
      </p>
      <p v-if="profileSaved" class="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-2.5 text-body-sm text-emerald-400">
        Profile saved to this browser. Changes persist across reloads.
      </p>
      <p v-if="profileError" class="rounded-lg border border-destructive/30 bg-destructive/10 p-2.5 text-body-sm text-destructive">
        {{ profileError }}
      </p>
      <p v-if="revokedMsg" class="rounded-lg border border-primary/30 bg-primary-container/10 p-2.5 text-body-sm text-primary">
        {{ revokedMsg }}
      </p>
      <p v-if="pwdMsg" class="rounded-lg border border-tertiary-container/30 bg-tertiary-container/10 p-2.5 text-body-sm text-tertiary">
        {{ pwdMsg }}
      </p>
      <p v-if="addressError" class="rounded-lg border border-destructive/30 bg-destructive/10 p-2.5 text-body-sm text-destructive">
        {{ addressError }}
      </p>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <!-- Left column -->
        <div class="space-y-6 lg:col-span-8">
          <!-- Account profile — now working -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-4 border-b border-outline-variant pb-4">
              <div class="flex size-14 items-center justify-center rounded-xl bg-primary-container font-heading text-xl font-bold text-on-primary-container">
                {{ initials }}
              </div>
              <div>
                <h2 class="font-heading text-headline-sm font-semibold text-on-surface">{{ displayName }}</h2>
                <p class="text-body-sm text-on-surface-variant">{{ displayEmail }}</p>
              </div>
              <span class="ml-auto rounded-lg border border-tertiary-container/30 bg-tertiary-container/10 px-2.5 py-1 text-label-md font-semibold text-tertiary">
                Shipper
              </span>
            </div>

            <form class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2" @submit.prevent="persistProfile">
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Organization</span>
                <input v-model="saveProfile.organization" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface placeholder:text-outline focus:border-primary focus:outline-none" />
              </label>
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Email</span>
                <input :value="displayEmail" disabled class="mt-1 w-full cursor-not-allowed rounded-lg border border-outline-variant bg-surface-low px-3 py-2 font-body-md text-body-md text-on-surface-variant" />
              </label>
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Phone</span>
                <input v-model="saveProfile.phone" placeholder="+1 (212) 555-0148" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface placeholder:text-outline focus:border-primary focus:outline-none" />
              </label>
              <label class="block">
                <span class="text-label-md font-medium text-on-surface-variant">Time zone</span>
                <select v-model="saveProfile.timezone" class="mt-1 w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option v-for="tz in timezones" :key="tz" :value="tz">{{ tz }}</option>
                </select>
              </label>
              <div class="sm:col-span-2 flex items-center justify-end gap-2">
                <p class="mr-auto text-label-sm text-on-surface-variant">Saved to local storage — reload to verify persistence</p>
                <Button type="submit" class="rounded-lg bg-primary px-4 py-2 font-label-md font-bold text-on-primary-container hover:bg-primary/90" :disabled="profileSaving">
                  <MIcon name="save" class="text-[16px]" />
                  {{ profileSaving ? 'Saving…' : 'Save Changes' }}
                </Button>
              </div>
            </form>
          </section>

          <!-- Notification preferences — persisted -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2 border-b border-outline-variant pb-3">
              <MIcon name="notifications_active" class="text-[22px] text-primary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Notification Preferences</h2>
            </div>

            <div class="mt-3 flex items-center gap-2">
              <span class="text-label-md font-medium text-on-surface-variant">Deliver via</span>
              <button
                class="rounded-lg px-3 py-1 text-label-md font-semibold transition-colors"
                :class="channel === 'email' ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'"
                @click="channel = 'email'"
              >
                Email
              </button>
              <button
                class="rounded-lg px-3 py-1 text-label-md font-semibold transition-colors"
                :class="channel === 'sms' ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'"
                @click="channel = 'sms'"
              >
                SMS
              </button>
            </div>

            <ul class="mt-4 divide-y divide-outline-variant/60">
              <li v-for="pref in prefs" :key="pref.id" class="flex items-center justify-between gap-3 py-3">
                <div>
                  <p class="font-label-md font-semibold text-on-surface">{{ pref.title }}</p>
                  <p class="mt-0.5 text-body-sm text-on-surface-variant">{{ pref.description }}</p>
                </div>
                <Switch v-model:checked="pref.enabled" :aria-label="`Toggle ${pref.title}`" />
              </li>
            </ul>
            <p class="mt-3 text-label-sm text-on-surface-variant">Changes save automatically to this browser.</p>
          </section>

          <!-- Security — now working -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2 border-b border-outline-variant pb-3">
              <MIcon name="shield_lock" class="text-[22px] text-secondary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Security</h2>
            </div>

            <div class="mt-4 flex items-center justify-between gap-3 py-2">
              <div>
                <p class="font-label-md font-semibold text-on-surface">Two-factor authentication</p>
                <p class="text-body-sm text-on-surface-variant">Authenticator app or SMS code on login — persists locally</p>
              </div>
              <Switch v-model:checked="twoFactor" aria-label="Toggle two-factor authentication" />
            </div>

            <div class="mt-2 space-y-2 rounded-lg border border-outline-variant bg-surface-low p-4">
              <p class="text-label-md font-medium text-on-surface-variant">Active sessions</p>
              <ul>
                <li v-for="session in sessions" :key="session.device" class="flex items-center justify-between gap-2 py-1.5">
                  <div class="flex items-center gap-2 text-body-sm">
                    <MIcon :name="session.current ? 'laptop' : 'devices'" class="text-[18px] text-on-surface-variant" />
                    <span class="text-on-surface">{{ session.device }}</span>
                    <span class="text-on-surface-variant">· {{ session.location }}</span>
                    <span v-if="session.current" class="rounded border border-primary/30 bg-primary-container/10 px-1.5 py-0.5 text-label-sm font-semibold text-primary">This device</span>
                  </div>
                  <button v-if="!session.current" class="text-label-sm font-medium text-destructive transition-colors hover:underline" @click="revokeSession(session.device)">
                    Revoke
                  </button>
                </li>
                <li v-if="sessions.length === 0" class="py-2 text-center text-body-sm text-on-surface-variant">No other sessions.</li>
              </ul>
            </div>

            <button class="mt-4 inline-flex items-center gap-1.5 text-label-md font-semibold text-primary transition-colors hover:text-on-surface" @click="changePassword">
              <MIcon name="key" class="text-[18px]" />
              Change password
              <span class="text-label-sm font-normal text-on-surface-variant">(handled by SSO admin)</span>
            </button>
          </section>
        </div>

        <!-- Right column -->
        <div class="space-y-6 lg:col-span-4">
          <!-- Address book — persisted -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2 border-b border-outline-variant pb-3">
              <MIcon name="map" class="text-[22px] text-primary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Address Book</h2>
            </div>

            <ul class="mt-3 space-y-2">
              <li v-for="address in addresses" :key="address.id" class="rounded-lg border border-outline-variant bg-surface-low p-3">
                <div class="flex items-center justify-between gap-2">
                  <div class="flex items-center gap-2">
                    <span class="font-label-md font-semibold text-on-surface">{{ address.label }}</span>
                    <span v-if="address.isDefault" class="rounded border border-primary/30 bg-primary-container/10 px-1.5 py-0.5 text-label-sm font-semibold text-primary">Default</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <button v-if="!address.isDefault" class="rounded px-1.5 py-0.5 text-label-sm text-on-surface-variant transition-colors hover:text-primary" @click="setDefault(address.id)">
                      Use as default
                    </button>
                    <button class="rounded px-1.5 py-0.5 text-label-sm text-on-surface-variant transition-colors hover:text-destructive" @click="removeAddress(address.id)">
                      Remove
                    </button>
                  </div>
                </div>
                <p class="mt-1.5 text-body-sm text-on-surface-variant">{{ address.line1 }}{{ address.line2 ? `, ${address.line2}` : '' }}</p>
                <p class="text-body-sm text-on-surface-variant">{{ address.city }}, {{ address.zip }} · {{ address.country }}</p>
              </li>
            </ul>

            <button
              v-if="!addOpen"
              class="mt-3 flex w-full items-center justify-center gap-1.5 rounded-lg border border-dashed border-outline-variant py-2.5 text-label-md font-semibold text-primary transition-colors hover:border-primary/60 hover:bg-surface-container-high"
              @click="addOpen = true"
            >
              <MIcon name="add_location_alt" class="text-[18px]" />
              Add Address
            </button>

            <form v-else class="mt-3 space-y-2.5" @submit.prevent="addAddress">
              <input v-model="newAddress.label" placeholder="Label (e.g. Oakland Yard)" class="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface placeholder:text-outline focus:border-primary focus:outline-none" />
              <input v-model="newAddress.line1" placeholder="Street address" class="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface placeholder:text-outline focus:border-primary focus:outline-none" />
              <div class="grid grid-cols-2 gap-2.5">
                <input v-model="newAddress.city" placeholder="City" class="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface placeholder:text-outline focus:border-primary focus:outline-none" />
                <input v-model="newAddress.zip" placeholder="Postal code" class="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface placeholder:text-outline focus:border-primary focus:outline-none" />
              </div>
              <input v-model="newAddress.country" placeholder="Country" class="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface placeholder:text-outline focus:border-primary focus:outline-none" />
              <div class="flex items-center justify-end gap-2">
                <button type="button" class="text-label-md text-on-surface-variant hover:text-on-surface" @click="addOpen = false">Cancel</button>
                <Button class="rounded-lg bg-primary-container px-3 py-1.5 font-label-md font-bold text-on-primary-container hover:bg-primary" :disabled="!hasAddressInput()">
                  Save Address
                </Button>
              </div>
            </form>
          </section>

          <!-- Support — simplified (full Support page removed) -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2">
              <MIcon name="support_agent" class="text-[22px] text-tertiary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Support &amp; Contract</h2>
            </div>
            <p class="mt-2 text-body-sm leading-relaxed text-on-surface-variant">
              Your account is assigned a dedicated carrier-grade support channel with 24/7 track-and-trace escalation.
            </p>
            <div class="mt-4 space-y-2">
              <a class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5 transition-colors hover:border-primary/50" href="mailto:support@sheno.dev">
                <span class="flex items-center gap-2 text-label-md text-on-surface">
                  <MIcon name="mail" class="text-[18px] text-primary" />
                  support@sheno.dev
                </span>
                <MIcon name="arrow_outward" class="text-[16px] text-on-surface-variant" />
              </a>
              <a class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5 transition-colors hover:border-primary/50" href="#">
                <span class="flex items-center gap-2 text-label-md text-on-surface">
                  <MIcon name="description" class="text-[18px] text-primary" />
                  Service level agreement
                </span>
                <MIcon name="arrow_outward" class="text-[16px] text-on-surface-variant" />
              </a>
            </div>
          </section>
        </div>
      </div>
    </div>
  </main>
</template>
