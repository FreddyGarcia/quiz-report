let getQuestions = function () {

}

var app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        dt: null,
        columns: [
            { data: 'question_text', width: "40%", selected: true },
            { data: 'A' },
            { data: 'B' },
            { data: 'C' },
            { data: 'D' },
            { data: 'chose_a' },
            { data: 'chose_b' },
            { data: 'chose_c' },
            { data: 'chose_d' },
            { data: 'wrong', selected: true },
            { data: 'correct', selected: true },
            { data: 'attemps', selected: true },
            { data: 'percent_correct', selected: true },
            { data: 'airtable_id', selected: true },
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
    mounted() {
        axios
            .get('/questions')
            .then(response => {
                this.dt = $('#questions').DataTable({
                    dom: 'frBtip',
                    "pageLength": 8,
                    ajax: {
                        url: '/questions',
                        dataSrc: function(json) {
                            $('.spinner').css({'display' : 'none'});
                            return json
                        }
                    },
                    responsive: true,
                    processing: false,
                    // language: {
                    //     loadingRecords: '&nbsp;',
                    //     processing: '<div class="spinner"></div>'
                    // },
                    columns: this.columns,
                    buttons: [ { extend: 'excel', title: null, className: 'btn-light', text : 'Download as Excel' } ]
                })

                this.columns.forEach((col, i) => {
                    var column = this.dt.column(i);
                    column.visible(col.selected || false)
                });
            })
    }
})