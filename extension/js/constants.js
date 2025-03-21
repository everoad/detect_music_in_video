'use strict'

const ICONS = Object.freeze({
  PLAY: 'play',
  STOP: 'stop',
  NEXT: 'next',
  PREV: 'prev',
  AUTOPLAY: 'autoplay',
  AUTOPLAY_ACTIVE: 'autoplay_active',
  AUTOMOVE: 'automove',
  AUTOMOVE_ACTIVE: 'automove_active'
})

const STORAGE_KEYS = Object.freeze({
  AUTO_MOVE_VIDEO: 'automove',
  AUTOPLAY: 'autoplay',
  VIDEOS: 'videos',
  Y_VIDOES: 'y_videos',
  LAST_CALL_API_TIME: 'lastCallApiTime',
  Y_LAST_CALL_API_TIME: 'y_lastCallApiTime'
})

const TIMOONG_CHANNEL_ID = '26253bf7ed6b95832c40f4f43f6d049d'

const API_CONSTANTS = Object.freeze({
  CHZZK_VIDEO_API_URL: 'https://api.chzzk.naver.com/service/v3/videos/',
  CHZZK_VIDEO_LIST_API_URL: `https://api.chzzk.naver.com/service/v1/channels/${TIMOONG_CHANNEL_ID}/videos?sortType=LATEST&pagingType=PAGE&size=40&publishDateAt=&videoType=`,
  CHZZK_VIDEO_PAGE_URL: 'https://chzzk.naver.com/video/'
})

const APP_CONSTANTS = Object.freeze({
  MAX_RETRY_COUNT: 10,
  LOCAL_BASE_URL: 'http://127.0.0.1:8000'
})

const TEXT = Object.freeze({
  PLAY: '시작',
  PAUSE: '정지',
  NEXT: '다음 노래',
  PREV: '이전 노래',
  AUTOPLAY: '자동 시작 OFF',
  AUTOPLAY_ACTIVE: '자동 시작 ON',
  AUTOMOVE: '다음 영상 지동 재생 OFF',
  AUTOMOVE_ACTIVE: '다음 영상 자동 재생 ON',
  PLAYABLE: '다시듣기'
})

const EVENTS = Object.freeze({
  VIDEO_SELECTED: 'videoSelected',
  VIDEO_STOP: 'videoStop'
})