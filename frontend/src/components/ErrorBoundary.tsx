import React from 'react'

type State = { hasError: boolean; error?: any }

export default class ErrorBoundary extends React.Component<{ children: React.ReactNode }, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: any) {
    return { hasError: true, error }
  }

  componentDidCatch(error: any, info: any) {
    console.error('App crashed:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 24 }}>
          <h2>Ошибка приложения</h2>
          <p style={{ color: 'crimson' }}>
            {(this.state.error?.message as string) || 'Неизвестная ошибка'}
          </p>
          <p style={{ fontSize: 12, opacity: 0.7 }}>
            Откройте DevTools → Console/Network для деталей.
          </p>
          <a href="/" style={{ textDecoration: 'underline' }}>Перезагрузить</a>
        </div>
      )
    }
    return this.props.children
  }
}
