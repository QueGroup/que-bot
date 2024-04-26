import Button from "../Button/Button.jsx";
import {useTelegram} from "../../hooks/UseTelegram.js";
import './Header.css'

const Header = () => {
    const {user, onClose} = useTelegram();

    return (
        <div className={"header"}>
            <Button onClick={onClose}>Закрыть</Button>
            <span>
                {user?.username}
            </span>
        </div>
    )
}

export default Header;