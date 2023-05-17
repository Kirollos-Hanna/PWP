/* eslint-disable */
import React from 'react';
import {Authorization} from './categoriesScreen.jsx'
import { useTable } from 'react-table'
import {

  Link
} from 'react-router-dom';

export const ProductsTable = (props) => {
   const data = React.useMemo(
     () => [
       {
         col1: '1',
         col2: 'Fender stratocaster',
         col3: '150.0',
         col4: 'Hyvä',
         col5: 'None',
         col6: 'Pekka',
         col7: '[]',
         col8: 'Instruments',
       },
     ],
     []
   )
 
   const columns = React.useMemo(
     () => [
       {
         Header: 'Id',
         accessor: 'col1', // accessor is the "key" in the data
       },
       {
         Header: 'Name',
         accessor: 'col2',
       },
       {
         Header: 'Price',
         accessor: 'col3',
       },
       {
         Header: 'Description',
         accessor: 'col4',
       },
       {
         Header: 'Images',
         accessor: 'col5',
       },
       {
         Header: 'User_name',
         accessor: 'col6',
       },
       {
         Header: 'Review',
         accessor: 'col7',
       },
       {
         Header: 'Categories',
         accessor: 'col8',
       },
     ],
     []
   )

   const {
     getTableProps,
     getTableBodyProps,
     headerGroups,
     rows,
     prepareRow,
   } = useTable({ columns, data})
   


   return (
    <div style={{
     flex: 1,
     display: 'inline-block',
     border: '1px solid grey',
     textAlign: 'left',
     paddingLeft: 10,
    }}>
    <div>

      <h1>Products</h1>
     <table {...getTableProps()}>
       <thead>
         {headerGroups.map(headerGroup => (
           <tr {...headerGroup.getHeaderGroupProps()}>
             {headerGroup.headers.map(column => (
               <th
                 {...column.getHeaderProps()}
                 style={{
                   background: 'aliceblue',
                   color: 'black',
                   fontWeight: 'bold',
                 }}
               >
                 {column.render('Header')}
               </th>
             ))}
           </tr>
         ))}
       </thead>
       <tbody {...getTableBodyProps()}>
         {rows.map(row => {
           prepareRow(row)
           return (
             <tr {...row.getRowProps()}>
               {row.cells.map(cell => {
                 return (
                   <td
                     {...cell.getCellProps()}
                     style={{
                       padding: '10px',
                       border: 'solid 1px gray',
                     }}
                   >
                     {cell.render('Cell')}
                   </td>
                 )
               })}
             </tr>
           )
         })}
       </tbody>
     </table>
     </div>
    </div>
   )
}

const ViewProductsByToken = (props) => {
    return(
     <div style={{display: 'inline-block', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{display: 'flex', flexDirection: 'row'}}>
        <a href=''>View all users</a>
        </div>
        <div>
          <li>
            <Link to="/api/categories/">View all categories</Link>
          </li>
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
        <div>
        <form>
        <label >
        View product
        <input type='text' name='product'/>
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

const NewProduct = (props) => {

  return(
  <div
    style={{
        alignItems: 'center',
        justifyContent: 'center',
        border: '1px solid black',
        display: 'inline-block',
        textAlign: 'center',
    }}>
    <h1>New product</h1>
    <div style={{textAlign: 'left', alignItems: 'left'}}>
        <form
        style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-around',
            justifyItems: 'center',
        }}>
            <div>
                <p>Name of product (required)</p>
                <label >
                <input type='text' name='name'/>
                </label>
            </div>

            <div>
                <p>Description</p>
                <label>
                <input type='text' name='description'/>
                </label>
            </div>
        </form>
    </div>

    <div style={{textAlign: 'left', alignItems: 'left'}}>
        <form
        style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-around',
            justifyItems: 'center',
        }}>
            <div>
                <p>Price (required)</p>
                <label >
                <input type='text' name='price'/>
                </label>
            </div>

            <div>
                <p>Images</p>
                <label>
                <input type='text' name='images'/>
                </label>
            </div>
        </form>
    </div>

    <div style={{textAlign: 'left', alignItems: 'left'}}>
        <form
        style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-around',
            justifyItems: 'center',
        }}>

            <div>
                <p>User_name (required)</p>
                <label >
                <input type='text' name='user_name'/>
                </label>
            </div>

            <div>
                <p>Categories</p>
                <label>
                <input type='text' name='categories'/>
                </label>
            </div>
        </form>
    </div>
    <input type='submit' value='Create a new product'/>
  </div>
  )
}

function ProductsScreen() {
    return(
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', alignItems: 'center', justifyItems: 'center', flexDirection: 'row'}}>
            <div style={{flex: 1,display: 'flex', flexDirection: 'column', height: '100%'}}>
                <div style={{display: 'flex', flexDirection: 'column', border: '1px solid black'}}>
                    <ProductsTable/>
                    <ViewProductsByToken/>
                </div>
                <NewProduct/>
            </div>
            <Authorization/>
        </div>
    )
}



export default ProductsScreen;
