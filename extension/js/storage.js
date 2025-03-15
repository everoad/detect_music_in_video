'use strict'

class StorageAdapter {
  static localStorageAdapter() {
    return {
      set: (data) => {
        return new Promise((resolve) => {
          Object.entries(data).forEach(([key, value]) => {
            window.localStorage.setItem(key, JSON.stringify(value))
          })
          resolve()
        })
      },
      get: (keys) => {
        return new Promise((resolve) => {
          const result = {}
          keys.forEach((key) => {
            const value = window.localStorage.getItem(key)
            result[key] = value ? JSON.parse(value) : null
          })
          resolve(result)
        })
      }
    }
  }

  static chromeStorageAdapter() {
    return {
      set: async (data) => {
        return new Promise((resolve) => {
          chrome.storage.local.set(data, resolve)
        })
      },
      get: async (keys) => {
        return new Promise((resolve) => {
          chrome.storage.local.get(keys, resolve)
        })
      }
    }
  }

  constructor() {
    this.storage = StorageAdapter.chromeStorageAdapter()
  }
  
  // 공통 저장 함수
  async set(key, value) {
    try {
      await this.storage.set({ [key]: value })
    } catch (e) {
      console.warn(e)
    }
  }

  // 공통 불러오기 함수
  async get(key, defaultValue = null) {
    try {
      const result = await this.storage.get([key])
      return result[key] !== undefined && result[key] !== null ? result[key] : defaultValue
    } catch (e) {
      console.warn(e)
      return defaultValue
    }
  }
}