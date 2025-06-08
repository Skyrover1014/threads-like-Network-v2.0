# Project Conventions

This document outlines the key conventions and architectural decisions for the Threads-like-Network v2.0 project. All contributors should follow these guidelines to maintain consistency.

## Documentation

- All files prefixed with `fyi-` must be placed in the root `/fyi` directory
- Documentation should be kept up-to-date with code changes
- Code comments should explain "why" rather than "what" when the code is complex

## Frontend (React)

- **Styling**: Use Tailwind CSS for all component and page styling. Do not use traditional CSS or CSS modules unless absolutely necessary (e.g., for third-party overrides).
  - Prefer utility classes directly in JSX for layout, spacing, colors, and responsiveness.
  - Extract repeated or complex class sets into reusable components or classnames helpers if needed.
  - Avoid writing custom CSS files for new styles; use Tailwind's configuration and utility classes.
- **Routing**:
  - **必須安裝 `react-router-dom`（不要只裝 `react-router`）**。
  - 所有路由元件（如 `<BrowserRouter>`、`<Link>`、`createBrowserRouter`、`RouterProvider` 等）和 Data Router API 都必須從 `react-router-dom` 匯入。
  - 路由定義應結構化為 JavaScript/TypeScript 物件陣列，並放在 `src/routes.ts` 或 `src/routes.tsx` 檔案中，集中管理。
  - 使用 Data Router pattern，善用 loader、action、error boundary 等功能。
  - Leverage React Router v7 features including loaders, actions, and error boundaries
  - Component structure should follow the separation of concerns principle
  - Use TypeScript for type safety

## Backend (Django)

- Built with Django Rest Framework (DRF) for API endpoints
- API documentation generated using Swagger/OpenAPI
- PostgreSQL as the primary database
- Follow RESTful conventions for API endpoints
- Authentication handled via JWT tokens

## General Coding Standards

- Use consistent formatting (enforced by linters)
- Write meaningful commit messages
- Keep components and functions small and focused on a single responsibility
- Test critical paths and components

## Development Workflow

- Feature branches should be created from the main branch
- Pull requests require at least one review before merging
- CI/CD pipeline must pass before merging to main 