import type React from "react";
import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { useNavigate } from "react-router";
import { apiClient } from "../lib/apiClient";


const UserForm: React.FC = () => {
    const [email, setEmail] = useState<string>("");
    const [pw, setPw] = useState<string>("");
    const params = useParams<{ email: string }>();
    const navigate = useNavigate();

    // ユーザーデータを取得する関数
    const fetchUser = async (email: string) => {
        const { data, error } = await apiClient.GET("/users/{email}", {
            params: {
                path: {
                    email: email
                }
            }
        })
        if (error) {
            console.error("Failed to fetch user data:", error);
            return <div>Error loading user data</div>;
        }
        if (data) {
            setEmail(data.email);
            setPw(data.pw);
        }
    }

    // 初回レンダリング時にユーザーデータを取得
    useEffect(() => {
        if (params.email) {
            fetchUser(params.email);
        }
    })

    // ユーザー更新処理
    const handleUpdate = async (email: string): Promise<boolean> => {
        const { error } = await apiClient.PUT("/users/{email}", {
            params: {
                path: {
                    email: email
                }
            },
            body: {
                pw: pw
            }
        })
        if (error) {
            console.error(`ユーザー ${email}の更新中にエラーが発生しました`, error);
            return false;
        }
        // ユーザー更新成功メッセージ
        alert(`ユーザー ${email} を更新しました`);

        return true;
    }

    // ユーザー作成処理
    const handleCreate = async (): Promise<boolean> => {
        const { data, error } = await apiClient.POST("/users/", {
            body: {
                email: email,
                pw: pw
            }
        })

        if (error) {
            console.error(`ユーザーの作成中にエラーが発生しました`, error);
            return false;
        }
        console.log("ユーザーの作成に成功しました", data);

        return true;
    }

    // フォーム送信処理
    const handlesubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        let result: boolean = false;
        if (params.email) {
            // 編集モード
            result = await handleUpdate(params.email);
        } else {
            // 新規登録モード
            result = await handleCreate();
        }

        if (result) {
            navigate("/users");
        }
    };

    // メールアドレスの変更ハンドラー
    const handleEmailChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setEmail(event.target.value);
        console.log(event.target.value);
    };

    // パスワードの変更ハンドラー
    const handlePwChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setPw(event.target.value);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-white gap-4">
            <h1 className="text-3xl font-bold">{params.email ? "ユーザー編集" : "ユーザー新規"}</h1>
            <form onSubmit={handlesubmit} className="flex flex-col gap-4 p-6 rounded shadow-md w-96 border-gray-100 border">
                <div className="flex flex-col">
                    <label
                        htmlFor="email"
                        className="font-bold mb-2 text-sm text-gray-700"
                    >
                        メールアドレス
                    </label>
                    <input type="email"
                        id="email"
                        name="email"
                        className="border border-gray-300 rounded px-3 py-2 hover:border-sky-500"
                        placeholder="example1@gmail.com"
                        value={email}
                        onChange={handleEmailChange}
                    />
                </div>
                <div className="flex flex-col">
                    <label
                        htmlFor="pw"
                        className="font-bold mb-2 text-sm text-gray-700"
                    >
                        パスワード
                    </label>
                    <input
                        type="password"
                        id="pw"
                        name="pw"
                        className="border border-gray-300 rounded px-3 py-2 hover:border-sky-500"
                        placeholder="8文字以上"
                        value={pw}
                        onChange={handlePwChange}
                    />
                </div>
                <button type="submit" className="text-white px-3 py-2 bg-blue-500 rounded-2xl hover:bg-blue-700">
                    {params.email ? "更新" : "登録"}
                </button>
            </form>
        </div>
    );
}
export default UserForm;