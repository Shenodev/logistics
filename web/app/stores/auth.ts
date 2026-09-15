import type { FetchError } from 'ofetch'
import {
  type LoginCredentials,
  type LoginResponse,
  type LogoutResponse,
  type SessionUser,
  type SignupCredentials,
} from '~~/shared/auth'

export type AuthStatus = 'idle' | 'pending' | 'authenticated' | 'unauthenticated'

interface AuthState {
  user: SessionUser | null
  status: AuthStatus
  loginError: string | null
}

function authRequest<T>(url: string, options: Record<string, unknown> = {}): Promise<T> {
  const base = String(useRuntimeConfig().public.apiBase ?? '').replace(/\/+$/, '')
  const target = base ? url : `/api${url}`
  const fetcher = import.meta.server ? useRequestFetch() : $fetch
  return fetcher<T>(target, {
    baseURL: base || undefined,
    credentials: base ? 'include' : 'same-origin',
    ...options,
  })
}

function getAuthErrorMessage(error: unknown): string {
  const fetchError = error as FetchError
  if (typeof fetchError?.data?.statusMessage === 'string') return fetchError.data.statusMessage
  if (typeof fetchError?.message === 'string') return fetchError.message
  return 'Authentication failed'
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    status: 'idle',
    loginError: null,
  }),

  getters: {
    isAuthenticated: (state) => state.status === 'authenticated',
    isPending: (state) => state.status === 'pending',
    role: (state) => state.user?.role ?? null,
    isAdmin: (state) => state.user?.role === 'admin',
    isUser: (state) => state.user?.role === 'user',
  },

  actions: {
    setSession(user: SessionUser) {
      this.user = user
      this.status = 'authenticated'
      this.loginError = null
    },

    clearSession() {
      this.user = null
      this.status = 'unauthenticated'
      this.loginError = null
    },

    async login(credentials: LoginCredentials): Promise<SessionUser> {
      this.status = 'pending'
      this.loginError = null

      try {
        const { user } = await authRequest<LoginResponse>('/auth/login', {
          method: 'POST',
          body: credentials,
        })
        this.setSession(user)
        return user
      }
      catch (error) {
        this.status = 'unauthenticated'
        this.loginError = getAuthErrorMessage(error)
        throw error
      }
    },

    async signup(credentials: SignupCredentials): Promise<SessionUser> {
      this.status = 'pending'
      this.loginError = null

      try {
        const { user } = await authRequest<LoginResponse>('/auth/signup', {
          method: 'POST',
          body: credentials,
        })
        this.setSession(user)
        return user
      }
      catch (error) {
        this.status = 'unauthenticated'
        this.loginError = getAuthErrorMessage(error)
        throw error
      }
    },

    async tryRefresh(): Promise<boolean> {
      try {
        await authRequest<Record<string, unknown>>('/auth/refresh', { method: 'POST' })
        return true
      }
      catch {
        return false
      }
    },

    async hydrate() {
      if (this.status !== 'idle') return

      this.status = 'pending'

      try {
        const { user } = await authRequest<LoginResponse>('/auth/me')
        this.setSession(user)
      }
      catch {
        const refreshed = await this.tryRefresh()
        if (!refreshed) {
          this.clearSession()
          return
        }

        try {
          const { user } = await authRequest<LoginResponse>('/auth/me')
          this.setSession(user)
        }
        catch {
          this.clearSession()
        }
      }
    },

    async logout() {
      try {
        await authRequest<LogoutResponse>('/auth/logout', { method: 'POST' })
      }
      catch {
        this.clearSession()
        return
      }

      this.clearSession()
    },
  },
})