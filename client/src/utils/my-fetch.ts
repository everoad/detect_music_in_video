interface MyRequestInit extends RequestInit {
  params?: Record<string, any>
}

function getParams(params: Record<string, any>) {
  return Object.keys(params).map(key => `${key}=${params[key]}`).join('&')
}

export function $fetch(input: string, init?: MyRequestInit) {
  input = init?.params ? `${input}?${getParams(init.params)}` : input
  return fetch(input, init)
}