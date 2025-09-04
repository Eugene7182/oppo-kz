import { describe, it, expect } from 'vitest'
import { getApiBase } from './http'

describe('getApiBase', () => {
  it('returns default API base URL when environment is not set', () => {
    expect(getApiBase()).toBe('https://oppo-kz.onrender.com')
  })
})

