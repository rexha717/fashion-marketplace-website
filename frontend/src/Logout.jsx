import { useEffect, useState } from 'react'
import { Brand } from './components.jsx'
import { logout } from './api.js'

export default function Logout() {
  const [state, setState] = useState('pending')

  useEffect(() => {
    let active = true
    logout()
      .then(() => active && setState('done'))
      .catch(() => active && setState('done'))
    return () => {
      active = false
    }
  }, [])

  return (
    <div className="screen">
      <Brand />
      <h1 className="title">
        {state === 'pending' ? 'Signing out' : 'Signed out'}
      </h1>
      {state === 'done' ? (
        <p className="swap">
          <a className="link" href="/">
            Return to the collection
          </a>
        </p>
      ) : null}
    </div>
  )
}
