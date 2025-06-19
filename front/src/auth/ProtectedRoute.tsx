import { Navigate, Outlet } from "react-router";
import { useAuthContext } from "./useAuthContext";

export const ProtectedRoute = () => {
    const { user, loading } = useAuthContext();

    
    if (loading) {
        return<div>Loading...</div>
    }

    if (user === null) {
        return <Navigate to={"/login"} replace />
    }

    return <Outlet />
}