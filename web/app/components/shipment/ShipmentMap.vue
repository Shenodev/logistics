<script setup lang="ts">
import type { Shipment } from '~~/app/data/shipments'

const props = defineProps<{ shipment: Shipment }>()

const labelFor = (kind: 'origin' | 'current' | 'checkpoint' | 'destination') =>
  props.shipment.waypoints.find((waypoint) => waypoint.kind === kind)?.label ?? ''
</script>

<template>
  <svg class="h-full w-full object-cover" fill="none" viewbox="0 0 1200 420" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <pattern height="40" id="grid" patternunits="userSpaceOnUse" width="40">
        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-opacity="0.6" stroke-width="0.75" />
      </pattern>
      <lineargradient id="routeGradient" x1="0%" x2="100%" y1="0%" y2="0%">
        <stop offset="0%" stop-color="#2861FF" />
        <stop offset="45%" stop-color="#06B6D4" />
        <stop offset="100%" stop-color="#334155" />
      </lineargradient>
      <radialgradient cx="50%" cy="50%" id="vesselGlow" r="50%">
        <stop offset="0%" stop-color="#06B6D4" stop-opacity="0.8" />
        <stop offset="100%" stop-color="#06B6D4" stop-opacity="0" />
      </radialgradient>
    </defs>

    <rect fill="#060e20" height="100%" width="100%" />
    <rect fill="url(#grid)" height="100%" width="100%" />

    <!-- Landmass silhouettes -->
    <path d="M 980 60 Q 1020 90 1000 150 T 960 210 T 1030 260 T 980 340 L 1180 380 L 1200 40 L 980 60 Z" fill="#131b2e" stroke="#1e293b" stroke-width="1.2" />
    <path d="M 900 120 Q 930 130 920 170 T 890 190 Z" fill="#171f33" stroke="#1e293b" stroke-width="1" />
    <path d="M 0 40 L 260 40 Q 240 100 220 160 T 260 230 T 280 310 T 210 390 L 0 420 Z" fill="#131b2e" stroke="#1e293b" stroke-width="1.2" />
    <path d="M 220 180 Q 260 190 280 230 T 240 280 Z" fill="#171f33" stroke="#1e293b" stroke-width="0.8" />

    <!-- Lat/Log overlay lines -->
    <line stroke="#1e293b" stroke-dasharray="4 6" stroke-width="0.8" x1="0" x2="1200" y1="140" y2="140" />
    <line stroke="#1e293b" stroke-dasharray="4 6" stroke-width="0.8" x1="0" x2="1200" y1="280" y2="280" />
    <line stroke="#1e293b" stroke-dasharray="4 6" stroke-width="0.8" x1="300" x2="300" y1="0" y2="420" />
    <line stroke="#1e293b" stroke-dasharray="4 6" stroke-width="0.8" x1="600" x2="600" y1="0" y2="420" />
    <line stroke="#1e293b" stroke-dasharray="4 6" stroke-width="0.8" x1="900" x2="900" y1="0" y2="420" />

    <!-- Great circle route -->
    <path d="M 950 150 Q 570 90 210 200" fill="none" stroke="url(#routeGradient)" stroke-linecap="round" stroke-width="3" />
    <path d="M 570 118 Q 380 145 210 200" fill="none" stroke="#475569" stroke-dasharray="6 6" stroke-width="2" />

    <!-- Origin -->
    <g transform="translate(950, 150)">
      <circle fill="#131b2e" r="6" stroke="#4cd7f6" stroke-width="2" />
      <circle fill="#4cd7f6" r="2.5" />
      <rect fill="#131b2e" height="24" rx="4" stroke="#3d494c" stroke-width="1" width="115" x="12" y="-22" />
      <text fill="#dae2fd" font-family="Inter" font-size="11" font-weight="600" x="20" y="-6">{{ labelFor('origin') }}</text>
    </g>

    <!-- Current waypoint -->
    <g transform="translate(570, 118)">
      <circle fill="url(#vesselGlow)" r="24" />
      <circle fill="#06b6d4" fill-opacity="0.2" r="12" stroke="#4cd7f6" stroke-dasharray="3 2" stroke-width="1.5" />
      <circle fill="#4cd7f6" r="4" />
      <path d="M 0 -8 L 3 -2 L 8 0 L 3 2 L 2 7 L 0 5 L -2 7 L -3 2 L -8 0 L -3 -2 Z" fill="#ffffff" />
      <rect fill="#131b2e" height="42" rx="6" stroke="#06b6d4" stroke-width="1.5" width="170" x="-85" y="-55" />
      <text fill="#4cd7f6" font-family="Inter" font-size="10" font-weight="700" x="-75" y="-38">{{ labelFor('current') }}</text>
      <text fill="#bcc9cd" font-family="Inter" font-size="10" x="-75" y="-23">POS: {{ shipment.lat }}, {{ shipment.lon }} • {{ shipment.spd }}</text>
      <path d="M -4 -13 L 0 -8 L 4 -13 Z" fill="#06b6d4" />
    </g>

    <!-- Intermediate checkpoint -->
    <g transform="translate(290, 175)">
      <circle fill="#171f33" r="4.5" stroke="#869397" stroke-width="1.5" />
      <rect fill="#131b2e" height="20" rx="3" stroke="#3d494c" stroke-width="0.8" width="90" x="-45" y="10" />
      <text fill="#bcc9cd" font-family="Inter" font-size="9" x="-38" y="24">{{ labelFor('checkpoint') }}</text>
    </g>

    <!-- Destination -->
    <g transform="translate(210, 200)">
      <circle fill="#131b2e" r="6" stroke="#869397" stroke-width="2" />
      <circle fill="#dae2fd" r="2" />
      <rect fill="#131b2e" height="24" rx="4" stroke="#3d494c" stroke-width="1" width="115" x="-125" y="-24" />
      <text fill="#dae2fd" font-family="Inter" font-size="11" font-weight="600" x="-117" y="-8">{{ labelFor('destination') }}</text>
    </g>
  </svg>
</template>