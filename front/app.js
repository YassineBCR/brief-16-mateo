fetch('http://127.0.0.1:8010/weather')
.then(response => {
    if (!response.ok) {
        throw new Error('Erreur réseau');
    }
    return response.json();
 })
 .then(data => {
    console.log(data);
    console.log('La connexion entre le frontend et l\'API a bien été effectuée.');
 })
 .catch(error => console.error('Erreur lors de la récupération des données:', error))