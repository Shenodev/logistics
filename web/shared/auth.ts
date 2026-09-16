export const SESSION_COOKIE = 'shenoflow_session'
export const REFRESH_COOKIE = 'shenoflow_refresh'

export type SessionRole = 'user' | 'admin' | 'driver'

export interface LoginCredentials {
  email: string
  password: string
}

export interface SignupCredentials {
  name: string
  email: string
  password: string
}

export interface SessionUser {
  id: string
  email: string
  name: string
  role: SessionRole
}

export interface SessionJwtPayload {
  sub: string
  email: string
  name: string
  role: SessionRole
  iat: number
  exp: number
}

export interface LoginResponse {
  user: SessionUser
}

export interface LogoutResponse {
  ok: boolean
}