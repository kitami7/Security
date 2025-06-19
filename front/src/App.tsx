import { Route, Routes } from "react-router"; // react-router-domからインポート
import Login from "./pages/Login";
import UserList from "./pages/UserList";
import UserForm from "./pages/UserForm";
import { ProtectedRoute } from "./auth/ProtectedRoute";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<UserForm />} />

      {/* 保護されたルート */}
      <Route element={<ProtectedRoute />}>
        <Route path="/users/:email" element={<UserForm />} />
        <Route path="/users" element={<UserList />} />
      </Route>
    </Routes>
  );
}

export default App;