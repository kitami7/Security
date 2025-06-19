import type React from "react";
import type { paths } from "../openapi-schema";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { apiClient } from "../lib/apiClient";

const UserList: React.FC = () => {
    const [users, setUsers] = useState<paths["/users/"]["get"]["responses"]["200"]["content"]["application/json"]>([]);
    const navigate = useNavigate();

    const fetchUsers = async () => {
        const { data, error } = await apiClient.GET("/users/", {});
        if (error) {
            console.error("Failed to fetch users:", error);
            return;
        }
        setUsers(data || []);
    };

    const handleDel = async (email: string) => {
        if (window.confirm(`ユーザー ${email} を削除しますか？`)) {

            const { error } = await apiClient.DELETE("/users/{email}", {
                params: {
                    path: {
                        email: email
                    }
                }
            })
            if (error) {
                console.error("Failed to delete user:", error);
                return;
            }
            // ユーザー削除成功メッセージ
            alert(`ユーザー ${email} を削除しました`);
        }
    }

    // 初回レンダリング時にユーザーデータを取得
    useEffect(() => {
        fetchUsers();
    }, []);

    return (
      <div className="flex flex-col items-center min-h-screen bg-white py-6 px-4">
        <div className="inline-block">
          {/* ヘッダー */}
          <div className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">
              ユーザー一覧
            </h1>
            <button
              className="self-start sm:self-auto px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700 transition cursor-pointer"
              onClick={() => navigate("/register")}
            >
              ＋ 新規登録
            </button>
          </div>

          {/* テーブル */}
          <table className="w-full border border-gray-300 rounded shadow-md table-auto inline-table">
            <thead className="bg-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-700">メールアドレス</th>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-700">パスワード</th>
                <th className="px-6 py-3 text-center text-sm font-bold text-gray-700">削除</th>
                <th className="px-6 py-3 text-center text-sm font-bold text-gray-700">編集</th>
              </tr>
            </thead>
            <tbody>
              {users.length > 0 ? (
                users.map((user) => (
                  <tr key={user.email} className="hover:bg-gray-100">
                    <td className="px-6 py-4 text-sm text-black">{user.email}</td>
                    <td className="px-6 py-4 text-sm text-black">{user.pw}</td>
                    <td className="px-6 py-4 text-center">
                      <button
                        className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-700 cursor-pointer"
                        onClick={() => handleDel(user.email)}
                      >
                        削除
                      </button>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button
                        className="px-3 py-2 bg-orange-500 text-white rounded hover:bg-orange-700 cursor-pointer"
                        onClick={() => navigate(`/users/${user.email}`)}
                      >
                        編集
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-4 text-center text-gray-500">
                    ユーザーが存在しません
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
}

export default UserList;