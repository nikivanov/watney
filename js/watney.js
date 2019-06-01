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
    const setVolume_throttled = _.throttle(setVolume, 500, {leading: true});

    $(document).keydown(function (event) {
        if (!$("#ttsSection").is(":visible")) {
            if (event.keyCode == 83) {
                $("#ttsSection").fadeIn(200);
                $("#ttsInput").focus();
                up = false;
                down = false;
                left = false;
                right = false;
                lookUp = false;
                lookDown = false;
                sendKeys();
                event.preventDefault();
                return;
            }

            if (event.keyCode == 86) {
                unmute();
                event.preventDefault();
                return;
            }

            if (event.key === '+' || event.key === '=' || event.key === '-') {
                let currentVolume = parseInt($("div#volumeSlider input").val());

                if (event.key === '+' || event.key === '=') {
                    currentVolume = currentVolume + 5;
                }
                else {
                    currentVolume = currentVolume - 5;
                }
                
                if (currentVolume > 100) {
                    currentVolume = 100;
                }
                else if (currentVolume < 0) {
                    currentVolume = 0;
                }
                
                $("div#volumeSlider input").val(currentVolume).trigger("input");
                event.preventDefault();
                return;
            }

            if (event.keyCode == 38) {
                up = true;
                event.preventDefault();
            }
            else if (event.keyCode == 40) {
                down = true;
                event.preventDefault();
            }
            else if (event.keyCode == 37) {
                left = true;
                event.preventDefault();
            }
            else if (event.keyCode == 39) {
                right = true;
                event.preventDefault();
            }
            else if (event.keyCode == 65) {
                lookDown = true;
                event.preventDefault();
            }
            else if (event.keyCode == 90) {
                lookUp = true;
                event.preventDefault();
            }

            sendKeys();
        }
    });

    $(document).keyup(function (event) {
        if (!$("#ttsSection").is(":visible")) {
            if (event.keyCode == 86) {
                mute();
                event.preventDefault();
                return;
            }

            if (event.keyCode == 38) {
                up = false;
                event.preventDefault();
            }
            else if (event.keyCode == 40) {
                down = false;
                event.preventDefault();
            }
            else if (event.keyCode == 37) {
                left = false;
                event.preventDefault();
            }
            else if (event.keyCode == 39) {
                right = false;
                event.preventDefault();
            }
            else if (event.keyCode == 65) {
                lookDown = false;
                event.preventDefault();
            }
            else if (event.keyCode == 90) {
                lookUp = false;
                event.preventDefault();
            }

            sendKeys();
        }
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
            $("#info").fadeOut(200);
        }
        else {
            $("#info").fadeIn(200);
        }
    });

    $("#infoButton").mouseleave(function (event) {
        $("#info").fadeOut(200);
    });

    $("#ttsButton").click(function (event) {
        if ($("#ttsSection").is(":visible")) {
            $("#ttsSection").fadeOut(200);
        }
        else {
            $("#ttsSection").fadeIn(200);
            $("#ttsInput").focus();
        }
    });

    $("#ttsInput").keydown(function (event) {
        if (event.keyCode == 27) {
            //escape
            event.preventDefault();
            $("#ttsInput").val("");
            $("#ttsSection").fadeOut(200);
        }
        else if (event.keyCode == 13) {
            //enter
            event.preventDefault();
            $("#ttsSection").animate({
                bottom: '80vh',
                opacity: '0'
            }, 200, function () {
                $("#ttsSection").hide();
                $("#ttsSection").css("bottom", "200px");
                $("#ttsSection").css("opacity", "1");
            });
            sendTTS($("#ttsInput").val());
        }
    });

    $("#ttsInput").blur(function (event) {
        $("#ttsInput").val("");
        $("#ttsSection").fadeOut(200);
    });

    $("#micButton").click(function (event) {
        if (videoroomPluginHandle) {
            if (videoroomPluginHandle.isAudioMuted()) {
                unmute();
            } else {
                mute();
            }
        }
    });

    $("div#volumeSlider input").on("input", function () {
        setVolume_throttled(this.value);
    });

    setupJoystick();

    doHeartbeat();

    doConnect();
});

var doVolumeSet = true;
function doHeartbeat() {
    $.ajax({
        url: '/heartbeat',
        type: "POST",
        dataType: "json"
    }).done(function (data) {
        $("#wifi_ssid").text(data.SSID);
        $("#wifi_quality").text(data.Quality);
        $("#wifi_signal").text(data.Signal);
        $("#cpuUsage").text(data.CPU);
        if (doVolumeSet) {
            $("div#volumeSlider input").val(data.Volume);
            doVolumeSet = false;
        }
    }).always(function () {
        setTimeout(doHeartbeat, 1000);
    });
}

function sendTTS(str) {
    $.ajax({
        url: '/sendTTS',
        type: "POST",
        data: JSON.stringify({ str }),
        contentType: "application/json; charset=utf-8",
        dataType: "json"
    });
}

function setVolume(volume) {
    $.ajax({
        url: '/setVolume',
        type: "POST",
        data: JSON.stringify({ volume }),
        contentType: "application/json; charset=utf-8",
        dataType: "json"
    });
}
