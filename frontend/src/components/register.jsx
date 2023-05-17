import React, { useState } from "react";
import { Link, useNavigate } from 'react-router-dom';
import axios from "axios";
import "./register.css";

// Registration Component
function Register() {
  let navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [image, setImage] = useState(null);
  const [role, setRole] = useState('Customer');

  const register = async () => {
    const user = { name, email, password, image, role };
    // Send a request to the registration endpoint in the backend
    // You should replace '/register' with your backend registration endpoint
    let res = await axios.post("http://127.0.0.1:5000/api/users/", user);
    // If registration is successful, redirect to the login page
      if (res.data.status === "success") {
        navigate('/login');
      }
  };

  const handleFileChange = (e) => {
    setImage(e.target.files[0]);
  };

  return (
    <div className="register-container">
        <h2 className="register-title">Register</h2>
        <input className="register-input" type="text" placeholder="Name" onChange={e => setName(e.target.value)} />
        <input className="register-input" type="email" placeholder="Email" onChange={e => setEmail(e.target.value)} />
        <input className="register-input" type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />

        <select className="register-select" value={role} onChange={e => setRole(e.target.value)}>
            <option value="Customer">Customer</option>
            <option value="Seller">Seller</option>
        </select>

        <button className="register-button" onClick={register}>Register</button>

        <p className="register-login">
            Already have an account? 
            <Link className="login-link" to="/login">Login here</Link>
        </p>
    </div>
  );
}

export default Register;
