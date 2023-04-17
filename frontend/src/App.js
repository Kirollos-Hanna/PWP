import React from 'react'
import './App.css';
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
    <div style={{border: '1px solid grey',
     flex: 1,
     alignItems: 'center',
     justifyContent: 'center',
     width: '50%',
    }}>
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
   )
}

function App() {
  return (
    <div className="App">
      <Categories/>
    </div>
  );
}

export default App;
