function get_tactic_data(eval_name) {
    restRequest('POST', {'index': 'tactic_data', 'eval': eval_name, 'data':'tactic'}, build_tactic_page);
}

function build_tactic_page(data){
    for (const [key, value] of Object.entries(data)) {
        build_tactic_html(key, value);
    }
}

function build_tactic_html(key, value) {

    let total_detections = 0;
    for (const [k, v] of Object.entries(value)){
        total_detections += v;
    }


    let h1_tag = document.createElement("h1");
    h1_tag.setAttribute("class", "card-title pricing-card-title")
    h1_tag.appendChild(document.createTextNode(total_detections));

    var card_body = document.getElementById(key);
    card_body.appendChild(h1_tag);

}




