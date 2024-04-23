import styled from 'styled-components';

export const Container = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 0 20px;
    background: radial-gradient(#9933ff, #6600cc);
`;

export const Form = styled.form`
    display: flex;
    flex-direction: column;
    width: 100%;
    max-width: 400px;
    background-color: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
`;

export const Label = styled.label`
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 8px;
`;

export const Input = styled.input`
    font-size: 16px;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-bottom: 16px;
    width: 100%;

    &:focus {
        outline: none;
        border-color: #9933ff;
    }
`;

export const SubmitButton = styled.button`
    font-size: 16px;
    font-weight: 500;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background-color: #9933ff;
    color: white;
    cursor: pointer;
    transition: background-color 0.3s;

    &:hover {
        background-color: #8022ee;
    }
`;
