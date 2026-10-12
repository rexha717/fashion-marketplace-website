export function Brand() {
  return (
    <a className="brand" href="/">
      Vellur&eacute;
    </a>
  )
}

export function Field({ label, name, type = 'text', value, onChange, error, autoComplete }) {
  return (
    <div className="field">
      <label className="label" htmlFor={name}>
        {label}
      </label>
      <input
        className="input"
        id={name}
        name={name}
        type={type}
        value={value}
        autoComplete={autoComplete}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? `${name}-error` : undefined}
        onChange={(event) => onChange(name, event.target.value)}
      />
      {error ? (
        <p className="field-error" id={`${name}-error`}>
          {error}
        </p>
      ) : null}
    </div>
  )
}

export function Alert({ errors }) {
  const messages = Object.values(errors ?? {}).flat()
  if (!messages.length) return null
  return (
    <div className="alert" role="alert">
      <ul>
        {messages.map((message) => (
          <li key={message}>{message}</li>
        ))}
      </ul>
    </div>
  )
}
