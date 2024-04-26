import "./LoginForm.css"
import React from "react";
import {appJSON} from "../../configs/AxiosConfig";
const LoginForm = () => {

    const [data, setData] = React.useState({login: "", password: ""});

    const handleData = (e, name) => {
        setData({...data, [name]: e.target.value});
    }

    async function sendData() {

        try {
            const response =  appJSON.post("http://127.0.0.1:8080/api/v1/auth/login/", data);

            if (response.status === 200) {
            console.log("SUCCESS");
            }

            return response.data;
        } catch {
            console.error("LOH");
        }
    }

    return (
        <div className="login-form">
            <form>
                <div>
                    <label htmlFor="username" className="login-form__label">Username</label>
                    <input type="text" id="username" name="username" value={data.login} onChange={(e) => handleData(e, "login")}/>
                </div>
                <div>
                    <label htmlFor="password" className="login-form__label">Password</label>
                    <input type="password" id="password" name="password" value={data.password} onChange={(e) => handleData(e, "password")}/>
                </div>
                <button type="submit" onClick={() => sendData()}>Login</button>
            </form>
        </div>
    )
}

export default LoginForm;
