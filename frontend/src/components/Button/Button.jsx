import './Button.css'

const Button = (props) => {
    return (
        // eslint-disable-next-line react/prop-types
        <button {...props} className={'button ' + props.className}/>
    )
}

export default Button;