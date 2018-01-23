$(document).ready(function () {
    $(".spinner").css('visibility','hidden');
    $('body').particleground({
        dotColor: '#8B8B8B',
        lineColor: '#8B8B8B',
        density: 12000,
        proximity: 100
    });
});


$('#chooseFile').bind('change', function () {
    var filename = $("#chooseFile").val();
    if (/^\s*$/.test(filename)) {
        $(".file-upload").removeClass('active');
        $("#noFile").text("No file chosen...");
    } else {
        $(".file-upload").addClass('active');
        $("#noFile").text(filename.replace("C:\\fakepath\\", ""));
        $(".spinner").css('visibility','visible');
        console.log("entered download");
        console.log(filename);
        var file = document.getElementById("chooseFile").files[0]
        var reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function () {
            $.ajax({
                type: "POST",
                url: "/upload",
                data: reader.result.split(',')[1],
                success: function(res) {
                    var decoded = atob(res);
                    console.log(decoded);
                    $(".spinner").css('visibility','hidden');
                    var hiddenElement = document.createElement('a');
                    hiddenElement.href = 'data:attachment/text,' + encodeURI(decoded);
                    hiddenElement.target = '_blank';
                    hiddenElement.download = 'latex.tex';
                    hiddenElement.click();
                }
            });
        };
    }}
);
