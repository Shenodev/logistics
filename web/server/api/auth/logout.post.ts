import { SESSION_COOKIE, type LogoutResponse } from '../../../shared/auth'

export default defineEventHandler((event): LogoutResponse => {
  deleteCookie(event, SESSION_COOKIE, sessionCookieOptions(event))
  return { ok: true }
})