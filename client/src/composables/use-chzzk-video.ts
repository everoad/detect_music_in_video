import { inject } from "vue"
import { ChzzkVideoKey } from "./chzzk-video.keys"


export function useChzzkVideo() {
  const context = inject(ChzzkVideoKey)

  if (!context) {
    throw new Error('useChzzkVideo must be used within a component where provideChzzkVideo is called')
  }

  return context

}