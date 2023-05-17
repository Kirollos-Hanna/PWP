import React from 'react';
import { Link } from 'react-router-dom';
import "./home.css";

function Home() {
  return (
    <div className="home">
      <h1>The most awesome app in the world</h1>
      <section>
        <h2>How to view the products page:</h2>
        <ol>
          <li>Click on the "View all products" link in the navigation bar at the top of the page.</li>
          <li>You will be taken to the products page.</li>
          <li>Here, you can browse through all our amazing products.</li>
        </ol>
        <Link className="nav-link" to="/api/users/products/">Go to Products Page</Link>
      </section>
    </div>
  );
}

export default Home;