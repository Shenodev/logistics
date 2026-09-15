import { SESSION_COOKIE, type LoginResponse, type SessionUser } from '../../../shared/auth'

export default defineEventHandler((event): LoginResponse | never => {
  const token = getCookie(event, SESSION_COOKIE)
  const session = token ? verifySession(event, token) : null

  if (!session) {
    throw createError({ statusCode: 401, statusMessage: 'Unauthorized' })
  }

  const user: SessionUser = {
    id: session.sub,
    email: session.email,
    name: session.name,
    role: session.role,
  }

  return { user }
})