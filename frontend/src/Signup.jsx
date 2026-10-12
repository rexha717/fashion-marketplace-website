import { useState } from 'react'
import { Alert, Brand, Field } from './components.jsx'
import { signup } from './api.js'

export default function Signup() {
  const [values, setValues] = useState({
    username: '',
    email: '',
    password: '',
    confirm_password: '',
  })
  const [errors, setErrors] = useState(null)
  const [pending, setPending] = useState(false)

  const handleChange = (name, value) => setValues((prev) => ({ ...prev, [name]: value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setPending(true)
    setErrors(null)
    try {
      await signup(values)
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
        Join the <em>house</em>
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
          label="Email"
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          error={errors?.email?.[0]}
          autoComplete="email"
        />
        <Field
          label="Password"
          name="password"
          type="password"
          value={values.password}
          onChange={handleChange}
          error={errors?.password?.[0]}
          autoComplete="new-password"
        />
        <Field
          label="Confirm password"
          name="confirm_password"
          type="password"
          value={values.confirm_password}
          onChange={handleChange}
          error={errors?.confirm_password?.[0]}
          autoComplete="new-password"
        />
        <button className="submit" type="submit" disabled={pending}>
          {pending ? 'Creating account…' : 'Create Account'}
        </button>
      </form>

      <p className="swap">
        Already have an account? <a href="/accounts/signin/">Sign in</a>
      </p>
    </div>
  )
}
