import React, { Component } from "react";
import "./App.css";
import CategoriesScreen from "./categoriesScreen.jsx";
import ProductScreen from "./productsScreen.jsx";
import ViewProductScreen from "./viewProductScreen";
import ViewProductsByInstrumentScreen from "./viewProductsInInstrumentsScreen";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Login from "./components/login";
import Register from "./components/register";
import Home from "./components/home";

class App extends Component {
  render() {
    return (
      <Router>
        <div className="App">
          <ul className="App-header nav-bar">
            <li>
              <Link className="nav-link" to="/categories">
                View all categories
              </Link>
            </li>
            <li>
              <Link className="nav-link" to="/products">
                View all products{" "}
              </Link>
            </li>
          </ul>
          <Routes>

            <Route
              exact
              path="/"
              element={<Home />}
            ></Route>
            <Route
              exact
              path="/categories/"
              element={<CategoriesScreen />}
            ></Route>
            
            <Route
              exact
              path="/products"
              element={<ProductScreen />}
            ></Route>
            <Route
              exact
              path="/login"
              element={<Login />}
            ></Route>
            <Route
              exact
              path="/register"
              element={<Register />}
            ></Route>
          </Routes>
        </div>
      </Router>
    );
  }
}

export default App;
