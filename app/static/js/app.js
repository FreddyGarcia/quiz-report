var app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        message: 'Hola Vue!'
    },
    mounted() {
        axios
            .get('/questions')
            .then(response => {
                console.log(response)
            })
    }
})