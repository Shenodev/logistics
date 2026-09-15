import type { SessionUser } from '../../shared/auth'

export interface DevAccount {
  id: string
  email: string
  password: string
  name: string
  role: SessionUser['role']
}

const devUsers = new Map<string, DevAccount>()

export function registerDevUser(account: DevAccount) {
  if (devUsers.has(account.email)) throw new Error('Email already registered')
  devUsers.set(account.email, account)
}

export function findDevUser(email: string): DevAccount | null {
  return devUsers.get(email) ?? null
}