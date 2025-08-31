:root {
    --section-blue: #4593ec;       
    --button-blue: #7bd1fc;        
    --input-bg: #cce6ff;           
    --light-bg: #fffdf5;           
    --text-blue: #1a3d7c;          
    --paper-bg: #fffdf5;           
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Georgia", "Times New Roman", serif;
}

body {
    margin: 0;
    font-family: "Georgia", "Times New Roman", serif;
    color: var(--text-blue);
    background: radial-gradient(circle at top left, #cce6ff, #ffffff 70%);
    min-height: 100vh;
}

header {
    text-align: center;
    font-size: 3em;
    font-weight: bold;
    color: var(--section-blue);
    letter-spacing: 2px;
    padding: 30px 0; 
}

.side-by-side-main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px 20px 50px 20px;
    display: flex;
    flex-wrap: nowrap;
    gap: 40px;
    justify-content: space-between;
}

.centered-main {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    display: flex;
    justify-content: center;
}

.section {
    background-color: var(--light-bg);
    border-radius: 22px;
    padding: 40px 30px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.08);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.section:hover {
    transform: translateY(-5px);
    box-shadow: 0 18px 35px rgba(0,0,0,0.12);
}

.side-by-side-main .section {
    flex: 0 0 40%;
    min-width: 320px;
    min-height: 450px;
}

.centered-main .section {
    flex: 0 0 100%;
    min-width: 320px;
    min-height: 450px;
}

form textarea, form select, form input[type="file"], 
.login-form input {
    width: 90%;
    padding: 14px;
    margin-bottom: 18px;
    border-radius: 12px;
    border: none;
    font-family: "Georgia", "Times New Roman", serif;
    color: var(--text-blue);
    background-color: var(--input-bg);
    transition: box-shadow 0.2s;
}

form textarea:focus, form select:focus, form input[type="file"]:focus,
.login-form input:focus {
    box-shadow: 0 0 8px var(--button-blue);
    outline: none;
}

button, .login-btn {
    background-color: var(--button-blue);
    color: var(--light-bg);
    padding: 16px 32px;
    border: none;
    border-radius: 14px;
    cursor: pointer;
    font-family: "Georgia", "Times New Roman", serif;
    font-weight: bold;
    letter-spacing: 0.5px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    transition: all 0.25s ease;
    margin-right: 20px;
}

button:last-child, .login-btn:last-child {
    margin-right: 0;
}

button:hover, .login-btn:hover {
    background-color: #85d0ff;
    transform: translateY(-3px);
    box-shadow: 0 8px 22px rgba(0,0,0,0.18);
}

.bottle_content {
    text-align: left;
    padding: 30px 35px;
    margin: 25px 0 0 0;
    border-radius: 18px;
    background-color: var(--paper-bg); 
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 1.2em;
    line-height: 1.8em;
    letter-spacing: 0.5px;
    color: var(--text-blue);
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.bottle_content img, .bottle_content video {
    max-width: 100%;
    display: block;
    margin: 12px auto 0;
    border-radius: 8px;
}

.bottle_content audio {
    width: 100%;
    margin-top: 12px;
    display: block;
}

.info {
    color: var(--section-blue);
    font-style: italic;
    text-align: left;
}

.empty-text {
    text-align: center;
    font-size: 1.2em;
    color: rgba(26, 61, 124, 0.8);
    padding: 60px 0;
}

.login-form {
    background: rgba(64, 64, 64, 0.15);
    border: 3px solid rgba(255, 255, 255, 0.3);
    padding: 30px;
    border-radius: 16px;
    backdrop-filter: blur(25px);
    text-align: center;
    color: white;
    width: 400px;
    box-shadow: 0px 0px 20px 10px rgba(0, 0, 0, 0.15);
}

.login-title {
    font-size: 40px;
    margin-bottom: 40px;
}

.input-box {
    margin: 20px 0;
    position: relative;
}

.input-box input {
    width: 100%;
    background: rgba(255, 255, 255, 0.1);
    border: none;
    padding: 12px 12px 12px 45px;
    border-radius: 99px;
    outline: 3px solid transparent;
    transition: 0.3s;
    font-size: 17px;
    color: white;
    font-weight: 600;
}

.input-box input::placeholder {
    color: rgba(255, 255, 255, 0.8);
    font-size: 17px;
    font-weight: 500;
}

.input-box input:focus {
    outline: 3px solid rgba(255, 255, 255, 0.3);
}

.input-box i {
    position: absolute;
    left: 15px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 20px;
    color: rgba(255, 255, 255, 0.8);
}

.remember-forgot-box {
    display: flex;
    justify-content: space-between;
    margin: 20px 0;
    font-size: 15px;
}

.remember-forgot-box label {
    display: flex;
    gap: 8px;
    cursor: pointer;
}
.remember-forgot-box input {
    accent-color: white;
    cursor: pointer;
}

.remember-forgot-box a {
    color: white;
    text-decoration: none;
}
.remember-forgot-box a:hover {
    text-decoration: underline;
}

.register {
    margin-top: 15px;
    font-size: 15px;
}
.register a {
    color: white;
    text-decoration: none;
    font-weight: 500;
}
.register a:hover {
    text-decoration: underline;
}

@media (max-width: 900px) {
    .side-by-side-main,
    .centered-main {
        flex-direction: column;
        gap: 30px;
    }

    .section {
        flex: 1 1 100%;
        min-width: auto;
    }

    form textarea, form select, form input[type="file"],
    .login-form input {
        width: 100%;
    }

    button, .login-btn {
        width: 100%;
        margin-right: 0;
        margin-bottom: 12px;
    }

    button:last-child, .login-btn:last-child {
        margin-bottom: 0;
    }
}
