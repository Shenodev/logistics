export const SESSION_COOKIE = 'shenoflow_session'

export const SESSION_COOKIE_OPTIONS = {
  httpOnly: true,
  secure: true,
  sameSite: 'lax' as const,
  path: '/',
  maxAge: 60 * 15,
}

export const REFRESH_COOKIE = 'shenoflow_refresh'

export const REFRESH_COOKIE_OPTIONS = {
  httpOnly: true,
  secure: true,
  sameSite: 'lax' as const,
  path: '/',
  maxAge: 60 * 60 * 24 * 7,
}

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
  role: 'user' | 'admin'
}

export interface SessionJwtPayload {
  sub: string
  email: string
  name: string
  role: 'user' | 'admin'
  iat: number
  exp: number
}

export interface LoginResponse {
  user: SessionUser
}

export interface LogoutResponse {
  ok: boolean
}