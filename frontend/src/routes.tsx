import type { RouteObject } from 'react-router';

import Layout from './Layout/Layout';
import HomePage from './pages/HomePage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import { loader as HomeLoader } from './loaders/HomeLoader';
import { loader as RegisterLoader } from './loaders/RegisterLoader';
import { loader as LoginLoader } from './loaders/LoginLoader';

import ErrorPage from './pages/ErrorPage';
import NotFoundPage from './pages/NotFoundPage';

const routes: RouteObject[] = [
    { 
        path: '/',
        element: <Layout />,
        children: [
            {
                path: '/',
                element: <HomePage />,
                loader: HomeLoader,
                errorElement: <ErrorPage />
            },
            {
                path: '/register',
                element: <RegisterPage />,
                loader: RegisterLoader,
                errorElement: <ErrorPage />
            },
            {
                path: '/login',
                element: <LoginPage />,
                loader: LoginLoader,    
                errorElement: <ErrorPage />
            },
            {
                path: '*',
                element: <NotFoundPage />,
                errorElement: <ErrorPage />
            }
        ]
    }
]

export default routes;