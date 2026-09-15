import { loadStripe, type Stripe, type StripeCardElement, type StripeElements } from '@stripe/stripe-js'

const CARD_STYLE = {
  base: {
    color: '#dae2fd',
    fontSize: '14px',
    fontFamily: "'Inter', ui-sans-serif, system-ui, sans-serif",
    '::placeholder': { color: '#869397' },
    ':-webkit-autofill': { color: '#dae2fd' },
  },
  invalid: {
    color: '#ffb4ab',
    iconColor: '#ffb4ab',
  },
}

export function useStripe() {
  const { public: { stripePk } } = useRuntimeConfig()

  const enabled = ref(Boolean(stripePk))
  const ready = ref(false)
  const loadError = ref<string | null>(null)
  const stripe = shallowRef<Stripe | null>(null)
  const elements = shallowRef<StripeElements | null>(null)
  const card = shallowRef<StripeCardElement | null>(null)

  async function init() {
    if (!enabled.value || ready.value || !import.meta.client) return
    try {
      const instance = await loadStripe(stripePk)
      if (!instance) throw new Error('Stripe failed to initialize')
      const els = instance.elements()
      stripe.value = instance
      elements.value = els
      card.value = els.create('card', { style: CARD_STYLE })
      ready.value = true
    }
    catch (error) {
      loadError.value = error instanceof Error ? error.message : 'Stripe failed to initialize'
      enabled.value = false
    }
  }

  function mountCard(node: HTMLElement | null) {
    if (!card.value || !node || card.value.mounted?.()) return
    card.value.mount(node)
  }

  function unmountCard() {
    card.value?.unmount()
  }

  return { enabled, ready, loadError, stripe, card, init, mountCard, unmountCard }
}