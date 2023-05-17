import React, { Component } from 'react';
import './App.css';
import CategoriesScreen from './categoriesScreen.jsx';
import ProductScreen from './productsScreen.jsx';
import ViewProductScreen from './viewProductScreen';
import ViewProductsByInstrumentScreen from './viewProductsInInstrumentsScreen';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link
} from 'react-router-dom';

class App extends Component {
  render() {
    return (
       <Router>
           <div className="App">
            <ul className="App-header">
              <li>
                <Link to="/api/categories/">View all categories</Link>
              </li>
              <li>
                <Link to="/api/users/products/">View all products </Link>
              </li>
            </ul>
           <Routes>
              <Route exact path='/api/categories/' element={< CategoriesScreen />}></Route>
              <Route exact path='/api/users/products/' element={< ProductScreen />}></Route>
              <Route exact path='/api/categories/products/' element={< ProductScreen />}></Route>


          </Routes>
          </div>
       </Router>
   );
  }

}

export default App;

