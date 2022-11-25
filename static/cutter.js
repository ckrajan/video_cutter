var collection_name;
var upload_file;
let video2;

var video_scr = document.getElementById('video_scr_id');
var ls = document.getElementById("list");
var export_csv = document.getElementById("export_csv");
var chop_upload_id = document.getElementById("chop_upload");

var time_arr = [];
var press = 0;
var counter = 0;
var split_name = 0;

var rows = [];
var rows_final = [];
var csv;
var spliced;
var clipname;
var clipname_arr = [];
var uploaded_file_name;
var encodedUri;
var final_csv;

$('#export_csv').click(function () {
    chop_upload_id.style.display = "block";
});


document.body.onkeyup = function (e) {
    if (e.key == "c" ||
        e.code == "KeyC" ||
        e.keyCode == 67
    ) {
        //your code
        uploaded_file_name = file_name;
        collection_name = collection_name_final;

        // collection_name = document.getElementById("collection").value;
        press++;
        export_csv.style.display = "block";

        var sec_num = parseInt(video_scr.currentTime, 10);
        var hours = Math.floor(sec_num / 3600);
        var minutes = Math.floor(sec_num / 60) % 60;
        var seconds = sec_num % 60;

        if (hours <= 9) {
            hours = '0' + hours;
        }
        if (minutes <= 9) {
            minutes = '0' + minutes;
        }
        if (seconds <= 9) {
            seconds = '0' + seconds;
        }

        if (hours == 0) {
            time_arr.push(minutes + ":" + seconds);
        } else {
            time_arr.push(hours + ":" + minutes + ":" + seconds);
        }

        if (press % 2 == 0) {

            if (counter == 0) {
                rows[counter] = ["File name", "Collection Name", "Split name", "Start time", "End time"];
            }

            counter++;
            console.log(time_arr);
            var start_time = time_arr[0];
            var end_time = time_arr[1];
            split_name++;
            ls.style.display = "block";
            ls.innerHTML += '<div id="box' + counter + '" style="color:rgb(31, 87, 37); font-size: 18px;"><i style="color:red; id="trash' + counter + '" class="fas fa-trash" onclick="removeItem(this);"></i> Collection: ' + collection_name + '; Split name: Clip_' + split_name + '; Start time: ' + start_time + '; End time: ' + end_time + '</div>';

            if (counter > 0) {
                rows[counter] = [uploaded_file_name, collection_name, "Clip_" + split_name, start_time, end_time];
            }

            while (time_arr.length > 0) {
                time_arr.pop();
            }
        }
    }
}

function removeItem(element) {
    var parent = element.parentNode;
    var thenum = parent.id.replace(/^\D+/g, '');

    clipname = rows[thenum];
    clipname_arr.push(clipname);

    var element = document.getElementById(parent.id)
    element.parentNode.removeChild(element); // will remove the element from DOM
}

async function send_timings() {
    const { request } = await axios.post("/chop_video", {
        rows_final: rows_final,
        filename: uploaded_file_name,
        contentType:
            "text/json"
    });

    return request
}

async function send_csv() {
    const { request } = await axios.post("/upload_csv", {
        csv: final_csv,
        filename: uploaded_file_name,
        contentType:
            "text/json"
    });

    return request
}

function csv_export() {

    rows_final = rows.filter(function (val) {
        return clipname_arr.indexOf(val) == -1;
    });

    rows_final.forEach(function (row) {
        csv += row.join(',');
        csv += "\n";
    });

    final_csv = csv.replace('undefinedFile name', 'File name');

    var csvContent = "data:text/csv;charset=utf-8," + final_csv + "\n";

    encodedUri = encodeURI(csvContent);

    var link = document.createElement("a");
    link.style.display = "none";
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "data_collection.csv");
    document.body.appendChild(link); // Required for FF

    link.click(); // This will download the data file named "data_collection.csv".

    var theRemovedElement = rows_final.shift();
}

function chop_upload() {
    send_timings();
    send_csv();
}



// This is that input field
const videoInput = document.getElementById('videoInput');

// This is the datalist
const datalist = document.getElementById('videoList');

function populateList(arr) {
    arr.forEach(country => {
        var option = document.createElement("option");
        option.innerHTML = country;
        datalist.appendChild(option);
    });
}

var video_list;

setTimeout(() => {
    var t = JSON.parse(video_list)
    populateList(t);
}, 1000);

// setTimeout(() => {
//     var datalist_value = document.getElementById('videoInput');
//     var ff = datalist_value.value;
// }, 2000);

get_uploaded_files()
    .then(result => video_list = result.responseText)
    .catch(error => console.error('Video id generated from client', error));


async function get_uploaded_files() {
    const { request } = await axios.post("/uploaded_files", {
        contentType:
            "text/json"
    });

    return request
}



// $("#upload-button").click(function () {
//     $("#upload").click();
// });

// $('#upload').change(function () {
//     // document.getElementById("upload").disabled = true;

//     upload_file = document.getElementById('upload').files[0];
//     upload_file_name = upload_file.name;
    // let videoMetaData = (upload_file) => {
    //     return new Promise(function (resolve, reject) {
    //         video_scr.addEventListener('canplay', function () {
    //             resolve({
    //                 video: video_scr,
    //                 height: video_scr.videoHeight,
    //                 width: video_scr.videoWidth
    //             });
    //         });
    //         video_scr.src = URL.createObjectURL(upload_file);
    //         document.body.appendChild(video_scr);
    //         video_scr.style.display = "block";
    //         video_scr.muted = false;
    //         video_scr.play();
    //         video_scr.controls = true;

    //         video_scr.autoplay = false;
    //         video_scr.height = 500;
    //         video_scr.width = 800;
    //         video_scr.position = "relative";
    //         video_scr.style.padding = "5px";
    //     })
    // }
    // videoMetaData($('#upload')[0].files[0]).then(function (value) {
    // })
// });