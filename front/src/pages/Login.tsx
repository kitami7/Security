import type React from "react";
import { useState } from "react";
import { apiClient } from "../lib/apiClient";
import { useNavigate } from "react-router";

const Login: React.FC = () => {
    const [email, setEmail] = useState<string>("");
    const [pw, setPw] = useState<string>("");
    const navigate = useNavigate();
    
    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
    
        const { error } = await apiClient.POST("/login", {
            body: {
                email: email,
                pw: pw
            }
        })
        if (error) {
            console.error(`ログイン中にエラーが発生しました`, error);
            return false;
        }

        navigate("/users");
    
    }

    const handleEmailChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setEmail(event.target.value);
        console.log(email);
    };

    const handlePwChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setPw(event.target.value);
        console.log(pw);
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-white gap-4">
            <h1 className="text-3xl font-bold">ログイン</h1>
            <form className="flex flex-col gap-4 p-6 rounded shadow-md w-96 border border-gray-500" onSubmit={handleSubmit}>
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
                {/* パスワードを忘れた場合のリンク */}
                <div className="text-right text-sm text-gray-500 hover:text-blue-500">
                    <a href="/forgot-password" className="hover:underline">パスワードを忘れた場合</a>
                </div>
                <button type="submit" className="text-white px-3 py-2 bg-blue-500 rounded-2xl hover:bg-blue-700">登録</button>
            </form>
        </div>
    );
}
export default Login;