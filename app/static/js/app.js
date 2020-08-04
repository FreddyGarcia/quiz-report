var socket = io();

var app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        dt: null,
        columns: [
            { data: 'question_text', width: "40%", selected: true },
            { data: 'A', width: "5%" },
            { data: 'B', width: "5%" },
            { data: 'C', width: "5%" },
            { data: 'D', width: "5%" },
            { data: 'chose_a', width: "5%" },
            { data: 'chose_b', width: "5%" },
            { data: 'chose_c', width: "5%" },
            { data: 'chose_d', width: "5%" },
            { data: 'wrong', width: "5%", selected: true },
            { data: 'correct', width: "5%", selected: true },
            { data: 'attemps', width: "5%", selected: true },
            { data: 'percent_correct', width: "5%", selected: true },
            { data: 'airtable_id', width: "10%", selected: true },
        ]
    },
    methods: {
        toogleVisible(col, index) {
            col.selected = col.selected;
            this.dt.column(index).visible(col.selected)
        },
        selectAll(){
            this.columns.map((col) => col.selected = true);
            this.columns.__ob__.dep.notify()

            this.dt.columns().visible(true);
        }
    },
})

socket.on('connect', function() {
    socket.emit('questions');

    socket.on('loaded', function(data){
        app.dt = $('#questions').DataTable({
            data : data,
            dom: 'frBtip',
            "pageLength": 8,
            responsive: true,
            processing: false,
            language: {
                loadingRecords: '&nbsp;',
                processing: '<div class="spinner"></div>'
            },
            columns: app.columns,
            buttons: [ { extend: 'excel', title: null, className: 'btn-light', text : 'Download as Excel' } ]
        })

        app.columns.forEach((col, i) => {
            var column = app.dt.column(i);
            column.visible(col.selected || false)
        });
    })
});
