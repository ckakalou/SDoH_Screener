export type UiIconName =
  | 'accessibility'
  | 'activity'
  | 'apple'
  | 'arrow-left'
  | 'arrow-right'
  | 'book'
  | 'briefcase'
  | 'briefcase-business'
  | 'bus'
  | 'building-2'
  | 'check'
  | 'clipboard-heart'
  | 'community-circle'
  | 'graduation-cap'
  | 'globe'
  | 'hand-heart'
  | 'health'
  | 'heart-pulse'
  | 'home'
  | 'house'
  | 'house-heart'
  | 'languages'
  | 'lock'
  | 'map'
  | 'map-pinned'
  | 'messages-square'
  | 'scale'
  | 'shield-plus'
  | 'shopping-basket'
  | 'smartphone'
  | 'sparkles'
  | 'support'
  | 'user'
  | 'user-round'
  | 'users-round'
  | 'wallet'
  | 'wallet-cards'
  | 'wifi'

interface UiIconProps {
  name: UiIconName
}

export function UiIcon({ name }: UiIconProps) {
  const sharedProps = {
    'aria-hidden': true,
    fill: 'none',
    viewBox: '0 0 24 24',
    xmlns: 'http://www.w3.org/2000/svg',
  }

  switch (name) {
    case 'accessibility':
      return <svg {...sharedProps}><circle cx="12" cy="4" r="2" /><path d="M5 8h14M12 6v7M8 21l4-8 4 8M7 12l-2 5M17 12l2 5" /></svg>
    case 'activity':
      return <svg {...sharedProps}><path d="M3 12h4l2.3-6 4.1 12 2.2-6H21" /></svg>
    case 'apple':
      return (
        <svg {...sharedProps}>
          <path d="M12 7c-4.6-3-8.4.2-7.7 5.2.7 5.1 3.3 8.1 5.4 7.2 1.4-.6 2.3-.6 3.7 0 2.1.9 4.7-2.1 5.4-7.2C19.5 7.3 16 4.2 12 7Z" />
          <path d="M12 7c-.2-2.1.8-3.7 3.1-4.7M12 7C10.6 5.4 9.1 4.8 7.4 5" />
        </svg>
      )
    case 'arrow-left':
      return <svg {...sharedProps}><path d="m14.5 18-6-6 6-6" /></svg>
    case 'arrow-right':
      return <svg {...sharedProps}><path d="m9.5 6 6 6-6 6" /></svg>
    case 'book':
      return <svg {...sharedProps}><path d="M4 5.5A3.5 3.5 0 0 1 7.5 2H11v17H7.5A3.5 3.5 0 0 0 4 22V5.5ZM20 5.5A3.5 3.5 0 0 0 16.5 2H13v17h3.5A3.5 3.5 0 0 1 20 22V5.5Z" /></svg>
    case 'briefcase':
    case 'briefcase-business':
      return <svg {...sharedProps}><rect x="3" y="7" width="18" height="13" rx="2" /><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18M10 12v2h4v-2" /></svg>
    case 'bus':
      return <svg {...sharedProps}><rect x="5" y="3" width="14" height="16" rx="3" /><path d="M7 13h10M8 19v2M16 19v2M8 7h8M8.5 16h.01M15.5 16h.01" /></svg>
    case 'building-2':
      return <svg {...sharedProps}><path d="M4 21V3h10v18M14 9h6v12M8 7h2M8 11h2M8 15h2M17 13h.01M17 17h.01M2 21h20" /></svg>
    case 'check':
      return <svg {...sharedProps}><path d="m5 12 4.2 4.2L19 6.5" /></svg>
    case 'clipboard-heart':
      return <svg {...sharedProps}><rect x="5" y="4" width="14" height="17" rx="2" /><path d="M9 4V3h6v1M12 17s-4-2.3-4-5a2.2 2.2 0 0 1 4-1.2A2.2 2.2 0 0 1 16 12c0 2.7-4 5-4 5Z" /></svg>
    case 'community-circle':
      return <svg {...sharedProps}><circle cx="12" cy="12" r="9" /><circle cx="12" cy="8" r="2" /><circle cx="7.5" cy="10.5" r="1.5" /><circle cx="16.5" cy="10.5" r="1.5" /><path d="M8.5 17c.4-2.1 1.5-3.2 3.5-3.2s3.1 1.1 3.5 3.2M4.8 15.5c.3-1.7 1.2-2.6 2.7-2.6.8 0 1.5.3 2 .8M19.2 15.5c-.3-1.7-1.2-2.6-2.7-2.6-.8 0-1.5.3-2 .8" /></svg>
    case 'graduation-cap':
      return <svg {...sharedProps}><path d="m2 9 10-5 10 5-10 5L2 9Z" /><path d="M6 11.2V16c3.5 2.7 8.5 2.7 12 0v-4.8M22 9v6" /></svg>
    case 'globe':
      return <svg {...sharedProps}><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c2.5 2.5 3.7 5.5 3.7 9S14.5 18.5 12 21M12 3C9.5 5.5 8.3 8.5 8.3 12s1.2 6.5 3.7 9" /></svg>
    case 'health':
      return <svg {...sharedProps}><path d="M20.8 5.7c-2.1-2.4-5.8-1.9-7.6.5L12 7.8l-1.2-1.6C9 3.8 5.3 3.3 3.2 5.7c-2 2.3-1.5 5.6.5 7.7L12 21l8.3-7.6c2-2.1 2.5-5.4.5-7.7Z" /><path d="M7 12h3l1-2.5 2 5 1-2.5h3" /></svg>
    case 'hand-heart':
      return <svg {...sharedProps}><path d="M3 15h4l3.2 3.2c.8.8 2 .9 2.9.3L21 13a2.2 2.2 0 0 0-2.8-3.4l-4.5 3M7 15V9H3" /><path d="M14 9s-3.5-2-3.5-4.2a1.9 1.9 0 0 1 3.5-1 1.9 1.9 0 0 1 3.5 1C17.5 7 14 9 14 9Z" /></svg>
    case 'heart-pulse':
      return <svg {...sharedProps}><path d="M20.8 5.7c-2.1-2.4-5.8-1.9-7.6.5L12 7.8l-1.2-1.6C9 3.8 5.3 3.3 3.2 5.7c-2 2.3-1.5 5.6.5 7.7L12 21l8.3-7.6c2-2.1 2.5-5.4.5-7.7Z" /><path d="M4.5 12H8l1.5-3 3 6 1.5-3h5.5" /></svg>
    case 'home':
    case 'house':
      return <svg {...sharedProps}><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1V10Z" /></svg>
    case 'house-heart':
      return <svg {...sharedProps}><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V10Z" /><path d="M12 17s-3-1.8-3-3.8a1.7 1.7 0 0 1 3-.9 1.7 1.7 0 0 1 3 .9c0 2-3 3.8-3 3.8Z" /></svg>
    case 'languages':
      return <svg {...sharedProps}><path d="M4 5h7M7.5 3v2M5 9c2.8-1 4.7-2.7 5.5-5M4 6c1.2 2.4 3.1 4.1 5.8 5M13 19l4-10 4 10M14.5 15h5" /></svg>
    case 'lock':
      return <svg {...sharedProps}><rect x="5" y="10" width="14" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3" /></svg>
    case 'map':
      return <svg {...sharedProps}><path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6ZM9 3v15M15 6v15" /></svg>
    case 'map-pinned':
      return <svg {...sharedProps}><path d="m3 6 5-2.5M16 5l5-2v15l-6 3-6-3-6 3V8" /><path d="M16 9c0 3-4 6-4 6s-4-3-4-6a4 4 0 1 1 8 0Z" /><circle cx="12" cy="9" r="1" /></svg>
    case 'messages-square':
      return <svg {...sharedProps}><path d="M7 16H5l-3 3V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v3" /><path d="M8 11a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v8l-3-3H10a2 2 0 0 1-2-2v-3Z" /></svg>
    case 'scale':
      return <svg {...sharedProps}><path d="M12 3v18M5 6h14M4 6 1.5 12h5L4 6ZM20 6l-2.5 6h5L20 6ZM7 21h10" /><path d="M1.5 12a2.5 2.5 0 0 0 5 0M17.5 12a2.5 2.5 0 0 0 5 0" /></svg>
    case 'shield-plus':
      return <svg {...sharedProps}><path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z" /><path d="M12 8v6M9 11h6" /></svg>
    case 'shopping-basket':
      return <svg {...sharedProps}><path d="M3 10h18l-2 9H5l-2-9ZM8 10l4-6 4 6M8 13v3M12 13v3M16 13v3" /></svg>
    case 'smartphone':
      return <svg {...sharedProps}><rect x="6" y="2" width="12" height="20" rx="2" /><path d="M10 5h4M11 18h2" /></svg>
    case 'sparkles':
      return <svg {...sharedProps}><path d="m12 3 1.2 3.8L17 8l-3.8 1.2L12 13l-1.2-3.8L7 8l3.8-1.2L12 3ZM19 14l.7 2.3L22 17l-2.3.7L19 20l-.7-2.3L16 17l2.3-.7L19 14ZM5 13l.8 2.2L8 16l-2.2.8L5 19l-.8-2.2L2 16l2.2-.8L5 13Z" /></svg>
    case 'support':
      return <svg {...sharedProps}><path d="M8.5 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM2 21a6.5 6.5 0 0 1 11.4-4.3" /><path d="M17.5 21s-4-2.4-4-5.2a2.2 2.2 0 0 1 4-1.3 2.2 2.2 0 0 1 4 1.3c0 2.8-4 5.2-4 5.2Z" /></svg>
    case 'user':
    case 'user-round':
      return <svg {...sharedProps}><circle cx="12" cy="7" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></svg>
    case 'users-round':
      return <svg {...sharedProps}><circle cx="9" cy="8" r="3" /><circle cx="17" cy="9" r="2.5" /><path d="M2.5 20a6.5 6.5 0 0 1 13 0M14 15a5 5 0 0 1 7.5 4.3" /></svg>
    case 'wallet':
    case 'wallet-cards':
      return <svg {...sharedProps}><path d="M4 6.5V5a2 2 0 0 1 2-2h12v4M4 6.5h15a2 2 0 0 1 2 2V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8.5a2 2 0 0 1 1-2Z" /><path d="M16 13h5M17 13h.01" /></svg>
    case 'wifi':
      return <svg {...sharedProps}><path d="M4.5 9a12 12 0 0 1 15 0M7.5 12.5a7.2 7.2 0 0 1 9 0M10.5 16a2.5 2.5 0 0 1 3 0" /><circle cx="12" cy="19" r="1" /></svg>
  }
}
