import { SESSION_COOKIE, SESSION_COOKIE_OPTIONS, type SessionJwtPayload } from '~~/shared/auth'

export function useAuthCookie() {
  return useCookie<SessionJwtPayload | null>(SESSION_COOKIE, SESSION_COOKIE_OPTIONS)
}