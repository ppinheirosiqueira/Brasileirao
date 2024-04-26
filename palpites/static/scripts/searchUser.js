function searchUsers() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    const results = document.getElementById('searchResults');
    results.innerHTML = '';

    const filteredUsers = userList.filter(user => user.toLowerCase().includes(input));

    if (input.length > 2){
        filteredUsers.forEach(user => {
            const li = document.createElement('li');
            li.textContent = user;
            li.addEventListener('click', () => selectUser(user));
            results.appendChild(li);
        });
    }
}

function selectUser(user) {
    document.getElementById('searchInput').value = user
}

function convidarPessoa(){
    const input = document.getElementById('searchInput').value;

    if (!userList.includes(input)){
        alert("Usuário não encontrado")
        return
    }

    fetch('../convidarPessoa/' + idGrupo + '/' + input)
    .then(function(response) {
        return response.json()
    })
    .then(function(data) {
        alert(data['mensagem'])
    })
    .catch(function(error) {
        console.log('Ocorreu um erro:', error)
    })
}