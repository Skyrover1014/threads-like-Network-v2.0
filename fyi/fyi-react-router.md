# React Router v7 - 關鍵概念與實作指南

## 路由模式比較

React Router v7 提供兩種主要的路由模式：

### 1. 宣告式路由 (Declarative Router)

- 路由直接寫在 JSX 中
- 使用 `<BrowserRouter>`、`<Routes>`、`<Route>` 組件
- 適合簡單頁面，功能較基本

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/profile/:userId" element={<ProfilePage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### 2. Data Router (推薦)

- 路由結構寫成 JS 物件陣列
- 使用 `createBrowserRouter` 和 `RouterProvider`
- 支援 loader、action、errorElement 等進階功能
- 適合中大型專案，有資料預取、錯誤處理需求

```tsx
// routes.tsx
const routes = [
  {
    path: '/',
    element: <HomePage />,
    loader: homeLoader,
    errorElement: <ErrorPage />
  },
  {
    path: '/profile/:userId',
    element: <ProfilePage />,
    loader: profileLoader,
    errorElement: <ErrorPage />
  }
];

// App.tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import routes from './routes';

const router = createBrowserRouter(routes);
export default function App() {
  return <RouterProvider router={router} />;
}
```

## 路由結構設計

### 基本路由

```tsx
const routes = [
  {
    path: '/',
    Component: HomePage,
    loader: homeLoader,
    errorElement: <ErrorPage />
  },
  {
    path: 'login',
    Component: LoginPage,
    loader: loginLoader
  }
];
```

### 巢狀路由與 Layout

```tsx
const routes = [
  {
    path: '/',
    element: <Layout />,
    children: [
      { path: '', element: <HomePage /> },
      { path: 'profile/:userId', element: <ProfilePage /> },
      { path: 'following/:userId', element: <FollowingPage /> }
    ]
  }
];

// Layout.jsx
import { Outlet } from 'react-router-dom';

function Layout() {
  return (
    <div>
      <Nav />
      <main>
        <Outlet /> {/* 子路由內容會顯示在這裡 */}
      </main>
    </div>
  );
}
```

## 進階功能

### 1. Data Loading (資料預取)

```tsx
// routes.tsx
{
  path: '/profile/:userId',
  element: <ProfilePage />,
  loader: async ({ params }) => {
    // 頁面載入前先獲取資料
    const userData = await fetchUser(params.userId);
    return userData;
  }
}

// ProfilePage.jsx
import { useLoaderData } from 'react-router-dom';

function ProfilePage() {
  // 自動獲取 loader 返回的資料
  const userData = useLoaderData();
  return <div>{userData.name}</div>;
}
```

### 2. 錯誤處理

```tsx
{
  path: '/profile/:userId',
  element: <ProfilePage />,
  loader: profileLoader,
  // 當路由或 loader 出錯時顯示
  errorElement: <ErrorPage />
}
```

### 3. 表單處理與資料提交

```tsx
{
  path: '/profile/:userId',
  element: <ProfilePage />,
  loader: profileLoader,
  // 處理表單提交
  action: async ({ request, params }) => {
    const formData = await request.formData();
    const result = await updateProfile(params.userId, formData);
    return result;
  }
}
```

### 4. 導航狀態與 Loading UI

```jsx
import { useNavigation } from 'react-router-dom';

function Layout() {
  const navigation = useNavigation();
  
  return (
    <div>
      {/* 導航過程中顯示 loading 狀態 */}
      {navigation.state === 'loading' && <LoadingBar />}
      <Outlet />
    </div>
  );
}
```

## 從傳統 SPA 遷移到 React Router

從原本的 Django + JS 架構轉換為 React Router 需注意：

1. **網址會變化** - 每個頁面對應一個 URL，有利於 SEO、分享、瀏覽器歷史
2. **組件化結構** - 將頁面拆分為多個 React 組件，而非操作 DOM
3. **條件渲染** - 使用 JSX 條件語法 `{condition && <Component />}`，而非 DOM 顯示/隱藏
4. **資料獲取** - 使用 loader 或 useEffect，而非手動 fetch 後更新 DOM

## 學習資源

- [React Router 官方文檔](https://reactrouter.com/)
- YouTube 頻道：Academind、Web Dev Simplified、Traversy Media、Jack Herrington

## 總結

React Router v7 提供了強大的路由管理功能，特別是 Data Router 模式適合中大型專案開發。通過 loader、action、errorElement 等功能，可以更優雅地處理資料獲取、表單提交和錯誤處理，提升用戶體驗。 