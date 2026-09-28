import Signin from './Signin.jsx'
import Signup from './Signup.jsx'
import Logout from './Logout.jsx'

const SCREENS = {
  signin: Signin,
  signup: Signup,
  logout: Logout,
}

export default function App() {
  // Django renders templates/auth.html with data-screen, so one bundle serves
  // every auth route without needing a client-side router.
  const screen = document.getElementById('root')?.dataset.screen ?? 'signin'
  const Screen = SCREENS[screen]

  if (!Screen) {
    return (
      <div className="screen">
        <h1 className="title">Unknown screen</h1>
      </div>
    )
  }

  return <Screen />
}
