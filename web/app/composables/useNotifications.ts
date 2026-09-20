export interface AppNotification {
  id: number
  kind: string
  title: string
  message: string
  stage_from: string
  stage_to: string
  order: number | null
  order_number: string | null
  is_read: boolean
  created_at: string
  time_ago?: string
}

interface FetchState {
  items: AppNotification[]
  unread: number
  loading: boolean
  error: string | null
}

function notifRequest<T>(url: string, options: Record<string, unknown> = {}): Promise<T> {
  const base = String(useRuntimeConfig().public.apiBase ?? '').replace(/\/+$/, '')
  const target = base ? url : `/api${url}`
  const fetcher = import.meta.server ? useRequestFetch() : $fetch
  return fetcher<T>(target, {
    baseURL: base || undefined,
    credentials: base ? 'include' : 'same-origin',
    ...options,
  } as any)
}

const state = reactive<FetchState>({
  items: [],
  unread: 0,
  loading: false,
  error: null,
})

const toasts = reactive<Array<{ id: number; title: string; message: string; order_number: string | null }>>([])

let es: EventSource | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null
let lastId = 0

export function useNotifications() {
  const isConnected = ref(false)

  async function fetchList(limit = 20) {
    state.loading = true
    try {
      const res = await notifRequest<{ results: AppNotification[]; unread_count: number }>('/api/notifications/', {
        method: 'GET',
        query: { limit },
      } as any)
      state.items = res.results ?? []
      state.unread = res.unread_count ?? state.items.filter((n) => !n.is_read).length
      if (state.items.length) lastId = Math.max(...state.items.map((n) => n.id), lastId)
      state.error = null
    } catch (e: any) {
      state.error = e?.data?.detail || e?.message || 'Failed to fetch notifications'
    } finally {
      state.loading = false
    }
  }

  async function markRead(id: number) {
    try {
      await notifRequest(`/api/notifications/${id}/read/`, { method: 'POST' })
      const n = state.items.find((x) => x.id === id)
      if (n) {
        n.is_read = true
        state.unread = Math.max(0, state.unread - 1)
      }
    } catch {}
  }

  async function markAllRead() {
    try {
      await notifRequest('/api/notifications/read-all/', { method: 'POST' })
      state.items.forEach((n) => (n.is_read = true))
      state.unread = 0
    } catch {}
  }

  function pushToast(n: AppNotification) {
    const id = n.id
    toasts.push({ id, title: n.title, message: n.message, order_number: n.order_number })
    // Auto-remove after 4s
    setTimeout(() => {
      const idx = toasts.findIndex((t) => t.id === id)
      if (idx !== -1) toasts.splice(idx, 1)
    }, 4000)
    // Haptic
    if (typeof navigator !== 'undefined' && 'vibrate' in navigator) (navigator as any).vibrate(20)
  }

  function handleIncoming(raw: any) {
    const n: AppNotification = {
      id: raw.id,
      kind: raw.kind,
      title: raw.title,
      message: raw.message,
      stage_from: raw.stage_from,
      stage_to: raw.stage_to,
      order: raw.order,
      order_number: raw.order_number,
      is_read: false,
      created_at: raw.created_at,
    }
    // De-dupe
    if (state.items.some((x) => x.id === n.id)) return
    state.items.unshift(n)
    state.unread++
    lastId = Math.max(lastId, n.id)
    pushToast(n)
  }

  function connectSSE() {
    if (typeof window === 'undefined') return
    if (es) return
    const base = String(useRuntimeConfig().public.apiBase ?? '').replace(/\/+$/, '')
    // Use $fetch base logic: if apiBase set, stream is absolute
    const url = base ? `${base}/api/notifications/stream/` : '/api/notifications/stream/'
    // Add last_id for resume
    const withId = lastId ? `${url}?last_id=${lastId}` : url
    try {
      // EventSource with credentials for HttpOnly JWT cookie
      es = new EventSource(withId, { withCredentials: true } as any)
      // @ts-ignore — TS doesn't know withCredentials on EventSource init, but browsers support it
      isConnected.value = false
      es.onopen = () => {
        isConnected.value = true
      }
      es.addEventListener('notification', (e: MessageEvent) => {
        try {
          const data = JSON.parse((e as any).data)
          handleIncoming(data)
        } catch {}
      })
      es.onmessage = (e: MessageEvent) => {
        // Generic message may also be notification
        if (e.data && e.data.startsWith('{')) {
          try {
            const data = JSON.parse(e.data)
            if (data.title) handleIncoming(data)
          } catch {}
        }
      }
      es.onerror = () => {
        isConnected.value = false
        // EventSource will auto-reconnect; also fallback to polling if needed
      }
    } catch {
      isConnected.value = false
    }
  }

  function disconnectSSE() {
    if (es) {
      es.close()
      es = null
      isConnected.value = false
    }
  }

  function startPolling() {
    if (pollTimer) return
    pollTimer = setInterval(() => {
      // If SSE is connected, we don't need polling, but keep as fallback
      if (!es || (es as any).readyState !== 1) {
        fetchList(20)
      }
    }, 5000)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  // Auto-connect when composable is used in setup
  if (typeof window !== 'undefined') {
    // Defer to onMounted to ensure auth is hydrated
    onMounted(() => {
      fetchList(20)
      connectSSE()
      startPolling()
    })
    onUnmounted(() => {
      disconnectSSE()
      stopPolling()
    })
  }

  return {
    items: computed(() => state.items),
    unread: computed(() => state.unread),
    loading: computed(() => state.loading),
    error: computed(() => state.error),
    toasts: computed(() => toasts),
    isConnected,
    fetchList,
    markRead,
    markAllRead,
    connectSSE,
    disconnectSSE,
  }
}
