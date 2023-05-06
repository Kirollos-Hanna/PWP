import React from 'react';
import {ProductsTable} from './productsScreen.jsx'

const ViewProductsByToken2 = (props) => {
    return(
     <div style={{display: 'inline-block', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{display: 'flex', flexDirection: 'row'}}>
        <a href=''>View all products</a>
        </div>

        <div>
        <form>
        <label >
        View products in 
        <input type='text' name='category'/>
        </label>
        <label style={{marginLeft: 20}}>
        Token 
        <input type='text' name='token'/>
        </label>
        <input type='submit' value='Submit'/>
        </form>
        </div>

        <div>
        <form>
        <label >
        View products by 
        <input type='text' name='user_name'/>
        </label>
        <label style={{marginLeft: 20}}>
        Token 
        <input type='text' name='token'/>
        </label>
        <input type='submit' value='Submit'/>
        </form>
        </div>

     </div>
    )
}

function ViewProductsByInstrumentScreen() {
    return(
        <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', justifyItems: 'center', flexDirection: 'row'}}>
            <div style={{flex: 1,display: 'flex', flexDirection: 'column', height: '100%'}}>
                <div style={{display: 'flex', flexDirection: 'column', border: '1px solid black'}}>
                    <ProductsTable/>
                    <ViewProductsByToken2/>
                </div>
            </div>
        </div>
    )
}

export default ViewProductsByInstrumentScreen;