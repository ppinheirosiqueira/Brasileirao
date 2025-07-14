import styles from './Header.module.css';

export default function Header() {
    const userName = "Nome do Usuário"; // No futuro, isso virá do seu backend

    return (
        <header className={styles.header}>
        <div className={styles.logo}>
            MeuSiteDePalpites
        </div>
        <nav className={styles.nav}>
            <span>Olá, {userName}</span>
            <a href="/perfil">Meu Perfil</a>
            <a href="/sair">Sair</a>
        </nav>
        </header>
    );
}