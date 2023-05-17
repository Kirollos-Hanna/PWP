import React, { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import "./login.css";

// Login Component
function Login() {
  let navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const login = async () => {
    const user = { email, password };
    // Send a request to the login endpoint in the backend
    let res = await axios.post('http://127.0.0.1:5000/api/users/auth/', user);
    // If login is successful, redirect to a new page
    console.log(res)
    if (res.data.auth_token) {
        console.log("got here")
      localStorage.setItem('auth-token', res.data.auth_token);
      navigate('/products');
    }
  };

  return (
    <div className="login-container">
        <h2 className="login-title">Login</h2>
        <input className="login-input" type="email" placeholder="Email" onChange={e => setEmail(e.target.value)} />
        <input className="login-input" type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
        <button className="login-button" onClick={login}>Login</button>

        <p className="login-register">
            Don't have an account? 
            <Link className="register-link" to="/register">Register here</Link>
        </p>
    </div>
  );
}

export default Login