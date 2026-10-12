import { useState } from 'react'
import { Alert, Brand, Field } from './components.jsx'
import { signin } from './api.js'

export default function Signin() {
  const [values, setValues] = useState({ username: '', password: '' })
  const [errors, setErrors] = useState(null)
  const [pending, setPending] = useState(false)

  const handleChange = (name, value) => setValues((prev) => ({ ...prev, [name]: value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setPending(true)
    setErrors(null)
    try {
      await signin(values)
      window.location.assign('/')
    } catch (error) {
      setErrors(error.fields)
      setPending(false)
    }
  }

  return (
    <div className="screen">
      <Brand />
      <h1 className="title">
        Welcome <em>back</em>
      </h1>

      <form className="card" onSubmit={handleSubmit} noValidate>
        <Alert errors={errors} />
        <Field
          label="Username"
          name="username"
          value={values.username}
          onChange={handleChange}
          error={errors?.username?.[0]}
          autoComplete="username"
        />
        <Field
          label="Password"
          name="password"
          type="password"
          value={values.password}
          onChange={handleChange}
          error={errors?.password?.[0]}
          autoComplete="current-password"
        />
        <button className="submit" type="submit" disabled={pending}>
          {pending ? 'Signing in…' : 'Sign In'}
        </button>
      </form>

      <p className="swap">
        No account yet? <a href="/accounts/signup/">Create one</a>
      </p>
    </div>
  )
}
