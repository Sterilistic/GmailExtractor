function get_lists() {
    // fetching the list of all labels 

    $.ajax({
        type: "GET",
        url: "/api/list_labels?format=json",
        success: function(labels) {
            var data = labels.sort();
            var select_labels = document.getElementById("all_labels");
            for (var i = 0; i < data.length; i++) {
                var label_list = document.createElement('li');
                label_list.setAttribute("class", "active ");
                var label_link = document.createElement('a');
                label_list.id = "label-" + data[i].id;
                var label_onclick = document.createAttribute("onclick");
                label_onclick.value = "switch_label(\"" + data[i].id + "\",\"" + data[i].name + "\");";
                label_list.setAttributeNode(label_onclick);
                label_link.innerHTML = (data[i].name).toUpperCase();
                label_link.href = '#';
                var link_onclick = document.createAttribute("onclick");
                link_onclick.value = "return false;";
                label_link.setAttributeNode(link_onclick);
                label_list.appendChild(label_link);
                select_labels.appendChild(label_list);

            }

        },
        error: function(data, errorThrown) {
            alert("Error:" + errorThrown + ":" + data);
        }
    });
}

function get_user() {

	//getting mthe user information

    $.ajax({
        type: "GET",
        url: "/api/get_user?format=json",
        success: function(data) {
            var current_user = document.getElementById('myName');
            var ico = document.createElement('i');
            ico.setAttribute("class", "fa fa-user");
            current_user.innerHTML = data;

        },
    });
}


function previous_current_mails(data) {
	//displaying the current mails 
    var current_mails = data;
    var mails_accordion = document.getElementById("mails_accordion");
    if (current_mails.length > 0) {
        mails_accordion.innerHTML = "";
        for (var i = 0; i < current_mails.length; i++) {
            // accordian list
            var accordion_defpan = document.createElement('div');
            accordion_defpan.setAttribute("class", "panel panel-default");
            var headpan = document.createElement('div');
            headpan.setAttribute("class", "panel-heading");
            headpan.setAttribute("role", "tab");
            headpan.setAttribute("id", "headingOne");
            var mailheading = document.createElement('h4');
            mailheading.setAttribute("class", "panel-title");

            /**Checkbox code **/
            var accordion_input = document.createElement("input");
            accordion_input.setAttribute("type", "checkbox");
            accordion_input.setAttribute("id", "" + current_mails[i].id);
            accordion_input.setAttribute("name", "greenCheck");
            accordion_input.setAttribute("class", "pinToggles");
            var checkclick = document.createAttribute("onclick");
            checkclick.value = "checkedmails(id)";
            accordion_input.setAttributeNode(checkclick);
            //checkbox code over



            var mail_link = document.createElement('a');
            mail_link.setAttribute("role", "button");
            mail_link.setAttribute("data-toggle", "collapse");
            mail_link.setAttribute("data-parent", "#mails_accordion");
            mail_link.setAttribute("href", "#mail_" + current_mails[i].id);
            mail_link.setAttribute("aria-expanded", "true");
            mail_link.setAttribute("id", "#mail_" + current_mails[i].id);
            mail_link.setAttribute("aria-controls", "collapseOne");

            if (current_mails[i].Subject == "") {
                mail_link.innerHTML = "(no subject)";
            } else {
                mail_link.innerHTML = current_mails[i].Subject;
            }
            var from_div = document.createElement('div');
            from_div.setAttribute("class", "pull-right");
            from_div.style.color = "#000";
            from_div.innerHTML = current_mails[i].From;
            mails_accordion.appendChild(accordion_defpan); //appending main block under predefined div in html
            mail_link.appendChild(from_div);
            //accordion_linmails[i].Subject == ""k{erHTML = mails[i].Subject;}
            var mail_body = document.createElement('div');
            mail_body.setAttribute("id", "mail_" + current_mails[i].id);
            mail_body.setAttribute("class", "panel-collapse collapse ");
            mail_body.setAttribute("aria-labelledby", "headingOne");
            var inner_div = document.createElement('div');
            inner_div.setAttribute("class", "panel-body container-fluid");
            var mailtext = document.createElement('p');
            mailtext.setAttribute("class", "span8");
            inner_div.appendChild(mailtext);
            mailtext.innerHTML = current_mails[i].body.html;
            mail_body.appendChild(inner_div);
            headpan.appendChild(mailheading);
            mailheading.appendChild(accordion_input);
            mailheading.appendChild(mail_link);
            accordion_defpan.appendChild(headpan);
            accordion_defpan.appendChild(mail_body);
        }
    } else {
        var norecordfound = document.getElementById("norecordfound");
        mails_accordion.innerHTML = "";
        //mails_accordion.innerHTML="<br/><span style=\"color:#636363\">No results found</span>"
        norecordfound.style.display = "";
    }
}







function display_error_message() {
	//if any error occured
    var loading_spinner = document.getElementById("loading_spinner");
    var loading_error = document.getElementById("loading_error");
    loading_spinner.style.display = "none";
    loading_error.style.display = "";
}


function bulk_download(label_id) {
	//handling bulk download request
    $.ajax({
        type: "GET",
        url: "/download/download_mails/?label=" + label_id,
        success: function(data){
		var modData = document.getElementById("reqresponse");		
		modData.innerHTML = data;	
	}

    });
}

function switch_label(label_id, label_name) {

	//handling switch label request

    document.getElementById("loading_error").style.display = "none";
    document.getElementById("norecordfound").style.display = "none";
    var mails_accordion = document.getElementById("mails_accordion");
    mails_accordion.innerHTML = "";
    spinner = document.getElementById("loading_spinner");
    spinner.style.display = "";
    var lname = document.getElementById("labelname");
    lname.innerHTML = "";
    lname.innerHTML = "Explore your digital data&nbsp;:&nbsp;" + label_name;
    var bulk_button = document.getElementById("bulk_download");
    bulk_button.setAttribute("onclick", "bulk_download(\"" + label_id + "\")");

    //calling the api to fetch mails
    $.ajax({
        type: "GET",
        url: "/api/list_mails/?format=json&label=" + label_id,
        success: function(data) {
            selected_mails = data;
            current_mails = selected_mails;
            previous_current_mails(current_mails)
            spinner.style.display = "none";
              


        },
        error: function(data, errorThrown) {
            display_error_message();
        }
    });



}


//bulk download function
function bulk_download_json(label_id) {
    $.msg({
        //autoUnblock : false,
        clickUnblock : false,
        beforeUnblock: function() {
            var self = this;
            $.ajax({
                type: "GET",
                url: "/initiate_download/?label=" + label_id,
                success: function(data) {

                    var bulk_mails = data;
                    bulk_download_filename = label_id.concat(".json");
                    var bulk_json_file = JSON.stringify(bulk_mails);
                    var a = window.document.createElement('a');
                    a.setAttribute("id","blkbtn");
                    a.href = window.URL.createObjectURL(new Blob([bulk_json_file], {
                        type: 'text/json'
                    }));
                    a.download = bulk_download_filename;

                    // Append anchor to body.
                    document.body.appendChild(a)
                    a.click();
                    // Remove anchor from body
                    document.body.removeChild(a)
                    document.getElementById(label_id).remove()
                    setTimeout(function(){
                        $("#jquery-msg-overlay").fadeOut(self.fadeOut,$("#jquery-msg-overlay").remove)
                    },1000);
                    remove_bulk_data(label_id);
                }
            });
        }
    });
}

function remove_bulk_data(label_id) {
	//removing unnecessary data in database
    $.ajax({
        type: "GET",
        url: "/remove_data/?label=" + label_id,

    });
}




function download_as_json() {
    // download few mails
    var json_filename = document.getElementById("json_filename").value;
    document.getElementById("json_content").innerHTML = "";

    if (json_filename == "") {
        download_filename = "filename.json";
    } else if (json_filename.slice(-5) == ".json") {
        download_filename = json_filename;
    } else {
        download_filename = json_filename.concat(".json");
    }
    var json_file = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(current_mails));
    $('<a id="json_link" href="data:' + json_file + '" download="' + download_filename + '">download JSON</a>').appendTo('#json_content');
    document.getElementById('json_link').click();
}




function filter_mails() {
    // filtering the mails on user input
    filter_input = document.getElementById("filter_input").value;
    current_mails = [];
    var words = filter_input.split(" ");
    var words_length = words.length
    var selected_length = selected_mails.length
    for (var i = 0; i < selected_length; i++) {
        for (var j = 0; j < words_length; j++) {
            if ((selected_mails[i].body.html.toLowerCase()).indexOf(words[j].toLowerCase()) != -1) {
                current_mails.push(selected_mails[i]);
                break;
            }
        }
    }
    var a = current_mails.length;
    display_current_mails(a);
}



function checkedmails(pass) {

    //user selected mails
    
    if (document.getElementById(pass).checked) {
        current_mails = [];
        //appending checked mails into current mails
        for (i = 0; i < selected_mails.length; i++) {
            if ((selected_mails[i].id === pass)) {
                current_mails.push(selected_mails[i]);
                break;
            }
        }
    } else {

        for (i = 0; i < current_mails.length; i++) {
            //removing unchecked mails from current_mails
            if (pass === current_mails[i].id) {
                current_mails.pop(current_mails[i]);

            }
        }

    }
}
