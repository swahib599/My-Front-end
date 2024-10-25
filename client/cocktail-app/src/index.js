import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './styles/main.css';
import App from './App';
import CocktailList from './Components/Cocktail/CocktailList';
import CocktailDetail from './Components/Cocktail/CocktailDetail';
import LoginForm from './Components/Auth/LoginForm';
import RegisterForm from './Components/Auth/RegisterForm';
import { ProtectedRoute } from './Components/Auth/ProtectedRoute';


const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        path: "/",
        element: <CocktailList />,
      },
      {
        path: "cocktails/new",
        element: (
          <ProtectedRoute>
            <CocktailDetail isNew={true} />
          </ProtectedRoute>
        ),
      },
      {
        path: "cocktails/:id",
        element: <CocktailDetail />,
      },
      {
        path: "login",
        element: <LoginForm />,
      },
      {
        path: "register",
        element: <RegisterForm />,
      },
    ],
  },
]);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);