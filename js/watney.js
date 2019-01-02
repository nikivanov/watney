var up = false;
var down = false;
var left = false;
var right = false;
var lookUp = false;
var lookDown = false;

var lastBearing = -1;
var lastLook = 0;

function sendKeys() {
    var bearing = "0";
    var look = 0

    if (up) {
        if (left) {
            bearing = "nw";
        }
        else if (right) {
            bearing = "ne";
        }
        else {
            bearing = "n";
        }
    }
    else if (down) {
        if (left) {
            bearing = "sw";
        }
        else if (right) {
            bearing = "se";
        }
        else {
            bearing = "s";
        }
    }
    else if (left) {
        bearing = "w";
    }
    else if (right) {
        bearing = "e";
    }

    if (lookUp) {
        look = 1;
    }
    else if (lookDown) {
        look = -1;
    }

    if (lastBearing != bearing || lastLook != look) {
        lastBearing = bearing;
        lastLook = look;
        var commandObj = {
            'bearing': bearing,
            'look': look
        };

        $.ajax({
            url: '/sendCommand',
            type: "POST",
            data: JSON.stringify(commandObj),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    }


}

$(document).ready(function () {
    $(document).keydown(function (event) {
        event.preventDefault();

        if (event.keyCode == 38) {
            up = true;
        }
        else if (event.keyCode == 40) {
            down = true;
        }
        else if (event.keyCode == 37) {
            left = true;
        }
        else if (event.keyCode == 39) {
            right = true;
        }
        else if (event.keyCode == 65) {
            lookDown = true;
        }
        else if (event.keyCode == 90) {
            lookUp = true;
        }

        sendKeys();
    });

    $(document).keyup(function (event) {
        event.preventDefault();

        if (event.keyCode == 38) {
            up = false;
        }
        else if (event.keyCode == 40) {
            down = false;
        }
        else if (event.keyCode == 37) {
            left = false;
        }
        else if (event.keyCode == 39) {
            right = false;
        }
        else if (event.keyCode == 65) {
            lookDown = false;
        }
        else if (event.keyCode == 90) {
            lookUp = false;
        }

        sendKeys();
    });

    $("#powerButton").click(function (event) {
        $("#shutdown-confirm").dialog({
            resizable: false,
            height: "auto",
            width: "auto",
            modal: true,
            buttons: {
                "Shut Down": function () {
                    $(this).dialog("close");
                    $.ajax({
                        url: '/shutDown',
                        type: "POST"
                    });
                },
                Cancel: function () {
                    $(this).dialog("close");
                }
            }
        });
    });

    $("#infoButton").click(function (event) {
        if ($("#info").is(":visible")) {
            $("#info").hide();
        }
        else {
            $("#info").show();
        }
    });

    doHeartbeat();

    doConnect();
});

function doHeartbeat() {
    $.ajax({
        url: '/heartbeat',
        type: "POST",
        dataType: "json"
    }).done(function (data) {
        $("#wifi_ssid").text(data.SSID);
        $("#wifi_quality").text(data.Quality);
        $("#wifi_signal").text(data.Signal);
    }).always(function () {
        setTimeout(doHeartbeat, 1000);
    });
}

