import "./LoginForm.css"
import React, {useCallback, useEffect} from "react";
import {useTelegram} from "../../hooks/UseTelegram.js";


const LoginForm = () => {

    const [data, setData] = React.useState({login: "", password: ""});
    const {tg} = useTelegram();
    const handleData = (e, name) => {
        setData({...data, [name]: e.target.value});
    }

    const onSendData = useCallback(() => {
        tg.sendData(JSON.stringify(data))
    }, [tg, data])
    useEffect(() => {
        tg.onEvent("mainButtonClicked", onSendData)
        return () => {
            tg.offEvent("mainButtonClicked", onSendData)
        }
    }, [tg, onSendData])

    useEffect(() => {
        tg.MainButton.setParams(
            {text: 'Войти'}
        )
    }, [tg])

    useEffect(() => {
        if (data.login === "" && data.password === "") {
            tg.MainButton.hide();
        } else {
            tg.MainButton.show();
        }
    })

    return (
        <div className="login-form">
            <form>
                <div>
                    <label htmlFor="username" className="login-form__label">Username</label>
                    <input type="text" id="username" name="username" value={data.login}
                           onChange={(e) => handleData(e, "login")}/>
                </div>
                <div>
                    <label htmlFor="password" className="login-form__label">Password</label>
                    <input type="password" id="password" name="password" value={data.password}
                           onChange={(e) => handleData(e, "password")}/>
                </div>
            </form>
        </div>
    )
}

export default LoginForm;
