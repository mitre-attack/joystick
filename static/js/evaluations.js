function getRoundEvals(round) {
    restRequest('POST', {'index': 'get_evals', 'round':round}, updateEvalSelect)
}

function savedToLog() {
    console.log('success')
}

function updateEvalSelect(data) {
    var options = [];
    options.push(`<option selected disabled> Select An Evaluation </option>`)
    data.forEach(
        element => {
           var option = `<option value=${element[0]}> ${element[1]} </option>`
           options.push(option);
        }
    )
    $('#evalsSelect').html(options);
    $('#evalsSelect').selectpicker('refresh');
}

function getEvalInfo(eval_name) {
        restRequest('POST', {'index': 'step_data', 'eval': eval_name, 'data':'step'}, build_step_chart);
        restRequest('POST', {'index': 'sub_step_data', 'eval': eval_name, 'data':'substep'}, build_sub_step_chart);
        restRequest('POST', {'index': 'mod_data', 'eval': eval_name, 'data':'modifier_detections'}, build_donuts);
        get_tactic_data(eval_name);
}


function load_charts() {
    var ctx = document.getElementById("stepChart");
    let step_bar_colors_APT3 = ["#185b85", "rgba(88, 88, 90, 1)", "rgba(237, 28, 36, 1)", "rgba(191, 30, 46, 1)", "rgba(130, 24, 44 ,1)", "rgba(167, 169, 172, 1)"];
    let step_bar_colors_APT29 = ["#185b85", "#007a9a", "#ffbb05", "#00978d", "#05ae6a", "#95bd2a"];
    let step_chart_labels = [];
    let step_chart_datasets = [];
}

function build_step_chart(data){
    var ctx = document.getElementById("stepChart");
    let step_bar_colors_APT29 = {None: '#185b85', Telemetry: '#007a9a', General: '#ffbb05', Technique: '#00978d', MSSP: '#05ae6a', 'N/A': '#95bd2a'}

    let datasets = [];

    for (const [key, value] of Object.entries(data.datasets)) {
        datasets.push(
            {
                label: key,
                data: value,
                backgroundColor: step_bar_colors_APT29[key]
            }
        )
    }

    build_chart(ctx, data.labels, datasets);
}


function build_sub_step_chart(data){
    var ctx = document.getElementById("subStepChart");
    let step_bar_colors_APT29 = {None: '#185b85', Telemetry: '#007a9a', General: '#ffbb05', Technique: '#00978d', MSSP: '#05ae6a', 'N/A': '#95bd2a'}

    let datasets = [];
    var i;
    for (const [key, value] of Object.entries(data.datasets)) {
        datasets.push(
            {
                label: key,
                data: value,
                backgroundColor: step_bar_colors_APT29[key]
            }
        )
    }
    build_chart(ctx, data.labels, datasets)
}

function build_donuts(data) {
    create_donut_with_legend();
    var div_modifiers_row = document.getElementById("div_modifiers_row");
    div_modifiers_row.innerHTML = '';
    for (const [key, value] of Object.entries(data.datasets)) {
        build_donut_chart(key, value);
    }
}

function build_chart(ctx, labels, datasets) {
        var stepChart = new Chart(ctx, {
        type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                scales: {
                    yAxes: [{ stacked: true, ticks: {beginAtZero: true, precision: 0}}],
                    xAxes: [{ stacked: true, ticks: {beginAtZero: true}}],
                }
            }
    });
}

var MODIFIERS = ["None",  "Alert", "Correlated", "Delayed (Manual)", "Delayed (Processing)", "Host Interrogation",
        "Residual Artifact",
        "Configuration Change (Detections)",
        "Configuration Change (UX)"]
let modifier_colors = ["#185b85", "#003f5c", "#374c80", "#7a5195", "#7a5195", "#bc5090", "#ef5675", "#ff764a", "#ff764a", "#ffa600"];

function build_donut_chart(key, value) {

    let chart_id = 'donutChart'.concat(key);
    var sum = value.reduce(function(a, b){
        return a + b;
    }, 0);
    if (sum > 0) {
        create_donut_chart_html(key);
        var ctx = document.getElementById(chart_id);
        var donutChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: MODIFIERS,
                datasets: [{
                    data: value,
                    backgroundColor: modifier_colors
                }]
            },
            options: {
                responsive: false,
                legend: {display: false}
            }
        });
   }
}

function create_donut_with_legend() {
    let legend_dataset = [];
    let legend_dummy_data = [];
        // Generate a zero for each modifier type to serve as dummy data for the legend "chart"
        MODIFIERS.forEach(item => {
            legend_dummy_data.push(0);
        })

        legend_dataset.push(
            {
                label: "Modifiers",
                data: legend_dummy_data,
                backgroundColor: modifier_colors,
                borderWidth: 1
            }
        );

        let ctx = document.getElementById('chart_modifiers_legend')
        var donutChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: MODIFIERS,
                datasets: legend_dataset
            },
            options: {
                legend: {
                    onClick: function (e) {
                        e.stopPropagation();
                    }
                }
            }
        });
}

function create_donut_chart_html(detection_type) {

    let div_col = document.createElement("div");
    div_col.setAttribute("class", "col-sm");
    div_col.setAttribute("style", "margin-top: 30px;")
    let div_row = document.createElement("div");
    div_row.setAttribute("class", "row");

    let canvas = document.createElement("canvas");
    canvas.setAttribute("width", "318");
    canvas.setAttribute("height", "150");
    canvas.setAttribute("id", "donutChart" + detection_type);

    div_row.appendChild(canvas);
    div_col.appendChild(document.createTextNode(detection_type));
    div_col.appendChild(div_row);
    div_modifiers_row.appendChild(div_col);
}

