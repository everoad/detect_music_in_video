import type { ChzzkVideo } from "@/types/chzzk";
import type { InjectionKey, Ref } from "vue";

interface ChzzkVideoContext {
  videos: Ref<ChzzkVideo[]>
  selectedVideo: Ref<ChzzkVideo | null>
  setSelectedVideo: (video: ChzzkVideo) => void
}


export const ChzzkVideoKey: InjectionKey<ChzzkVideoContext> = Symbol('CHZZK_VIDEO_INJECTION_KEY')