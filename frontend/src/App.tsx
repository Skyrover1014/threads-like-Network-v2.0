// import { useEffect,useState } from 'react'
// import './App.css'

// function App() {
//   const [data, setData] = useState(null)

//   const baseUrl = import.meta.env.VITE_API_BASE_URL

//   useEffect(() => {
//     fetch(`${baseUrl}/threads/`)
//       .then(res => res.json())
//       .then(setData)
//   }, [baseUrl])

//   return (
//     <>
//       <h1 className="text-3xl font-bold underline mb-4">
//         Hello world!
//       </h1>
//       <pre>{JSON.stringify(data)}</pre>
//     </>
//   )
// }

// export default App

import { createBrowserRouter } from 'react-router-dom';
import { RouterProvider } from 'react-router';
import routes from './routes';

const router = createBrowserRouter(routes);
export default function App() {
  return <RouterProvider router={router} />;
}