import Header from "./components/Header/Header.jsx";
import {Route, Routes} from "react-router-dom";
import LoginForm from "./components/LoginForm/LoginForm.jsx";
import React from "react";

function App() {

    return (
        <div className="App">
            <div className="login">
                <Header/>
                <Routes>
                <Route index element={<LoginForm/>}/>
            </Routes>
            </div>
        </div>
    );
}

export default App;
