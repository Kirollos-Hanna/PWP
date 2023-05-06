import React from 'react';
import { useTable } from 'react-table'

const Categories = (props) => {
   const data = React.useMemo(
     () => [
       {
         col1: '1',
         col2: 'None',
         col3: 'Instruments',
       },
       {
         col1: '2',
         col2: 'None',
         col3: 'Electronics',
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
         Header: 'Image',
         accessor: 'col2',
       },
       {
         Header: 'Name',
         accessor: 'col3',
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

      <h1>Categories</h1>
     <table {...getTableProps()} style={{ border: 'solid 1px blue' }}>
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
     <div>
      <a href=''>View all products</a>
     </div>
     </div>
     <div>
      <form>
      <label >
      View category
      <input type='text' name='category'/>
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

const NewCategory = (props) => {

  return(
  <div style={{flex: 1,textAlign: 'left', alignItems: 'left', paddingLeft: 20, paddingRight: 20, border: '1px solid black', display: 'inline-block'}}>
    <h1>New category</h1>
    <form>
    <p>Name of category (required)</p>
    <label >
      <input type='text' name='category'/>
    </label>
    <p>Image </p>
    <label>
    <input type='text' name='token'/>
    </label>
    </form>
    <input type='submit' value='Create new category'/>
  </div>
  )
}

export const Authorization = (props) => {
  return(
    <div style={{display: 'inline-block', border: '1px solid black', padding: 20}}>
      <h1>Authorization</h1>
      <form>
        <p>Name</p>
        <label>
        <input type='text' name='category'/>
        </label>

        <p>Email</p>
        <label>
        <input type='text' name='token'/>
        </label>

        <p>Password</p>
        <label>
        <input type='text' name='token'/>
        </label>

      </form>
      <input type='submit' value='Authorize'/>
      <p>Authorization status</p>
    </div>
  )
}

function CategoriesScreen() {
    return(
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', alignItems: 'center', justifyItems: 'center', flexDirection: 'row'}}>
            <div style={{flex: 1,display: 'flex', flexDirection: 'column', height: '100%'}}>
                <Categories/>
                <NewCategory/>
            </div>
            <Authorization/>
        </div>
    )
}

export default CategoriesScreen