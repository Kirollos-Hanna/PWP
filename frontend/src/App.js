import React from 'react'
import './App.css';
import CategoriesScreen from './categoriesScreen.jsx';
import ProductScreen from './productsScreen.jsx';
import ViewProductScreen from './viewProductScreen';
import ViewProductsByInstrumentScreen from './viewProductsInInstrumentsScreen';

function App() {
  return (
    <div className="App">
      <ViewProductsByInstrumentScreen/>
    </div>
  );
}

export default App;
