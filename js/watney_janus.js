var janusConnection;
var streamingPluginHandle;
var videoroomPluginHandle;
var publisherId;
var inputDevices;

function doConnect() {
    Janus.init({
        debug: true,
        dependencies: Janus.useDefaultDependencies(),
        callback: function () {
            onJanusInit();
        }
    });
}

function onJanusInit() {
    connectJanus();
}

function listDevices(devices) {
    const defaultDeviceId = getCookie("defaultDevice");

    const inputDevices = devices.filter(d => d.kind === 'audioinput');
    const inputDeviceOptions = inputDevices.map(d => $('<option value="' + d.deviceId + '">' + (d.label || d.deviceId) + '</option>'));

    $("#deviceSelector").find('option').remove().end();
    inputDeviceOptions.forEach(ido => $("#deviceSelector").append(ido));

    if (defaultDeviceId) {
        const defaultDevice = inputDevices.find(d => d.deviceId === defaultDeviceId);
        if(defaultDevice) {
            $("#deviceSelector").val(defaultDeviceId);
        }
    }

    $("#deviceSelector").change(audioDeviceChange);
    
}

function audioDeviceChange() {
    setCookie("defaultDevice", $('#deviceSelector').val(), 3650);
    if (videoroomPluginHandle) {
        unpublishOwnFeed();
    }
}

function connectJanus() {
    var server = null;
    if (window.location.protocol === 'http:')
        server = "http://" + window.location.hostname + ":8088/janus";
    else
        server = "https://" + window.location.hostname + ":8089/janus";

    janusConnection = new Janus({
        server: server,
        success: function () {
            onJanusConnect();
        },
        error: function (error) {
            alert("Janus server error: " + error);
        },
        destroyed: function () {

        }
    });
}

function onJanusConnect() {
    attachStreamingPlugin();
}

function attachStreamingPlugin() {
    var opaqueId = "streamingtest-" + Janus.randomString(12);
    janusConnection.attach({
        plugin: "janus.plugin.streaming",
        opaqueId: opaqueId,
        success: function (plugin) {
            streamingPluginHandle = plugin;
            streaming_onPluginAttached();
        },
        error: function (error) {
            console.log("Error attaching streaming plugin: " + error);
        },
        onremotestream: function (stream) {
            streaming_onRemoteStreamStart(stream);
        },
        onmessage: function (msg, jsep) {
            streaming_onRemoteMessage(msg, jsep);
        }
    });
}

function streaming_onRemoteStreamStart(stream) {
    var vidEl = $("#vid").get(0);
    Janus.attachMediaStream(vidEl, stream);
    attachVideoroomPlugin();
}

function streaming_onPluginAttached() {
    // Watney HD stream is id 10
    var body = { "request": "watch", id: 10 };
    streamingPluginHandle.send({ "message": body });
}

function streaming_onRemoteMessage(msg, jsep) {
    var result = msg["result"];
    if (result && result["status"] && result["status"] === 'stopped') {
        streaming_stopStream();
    }

    var error = msg["error"];
    if (error) {
        console.log("Remote error: " + error);
        streaming_stopStream();
    }

    if (jsep) {
        streamingPluginHandle.createAnswer({
            jsep: jsep,
            media: {
                audioSend: false,
                videoSend: false,
                data: true,
            },
            success: function (jsep) {
                var body = { "request": "start" };
                streamingPluginHandle.send({ "message": body, "jsep": jsep });
            },
            error: function (error) {
                console.log("Remote offer error: " + error);
            }
        });
    }
}

function streaming_stopStream() {
    if (streamingPluginHandle) {
        var body = { "request": "stop" };
        streamingPluginHandle.send({ "message": body });
        streamingPluginHandle.hangup();
    }
}

function attachVideoroomPlugin() {
    var opaqueId = "videoroom-" + Janus.randomString(12);
    janusConnection.attach({
        plugin: "janus.plugin.videoroom",
        opaqueId: opaqueId,
        success: function (plugin) {
            videoroomPluginHandle = plugin;
            videoroom_onPluginAttached();
        },
        error: function (error) {
            console.log("Error in videoroom plugin: " + error);
        },
        mediaState: function(medium, on) {
            Janus.log("Janus " + (on ? "started" : "stopped") + " receiving our " + medium);
        },
        onremotestream: function (stream) {
            
        },
        onlocalstream: function (stream) {
            mute();
        },
        onmessage: function (msg, jsep) {
            videoroom_onMessage(msg, jsep);
        },
        oncleanup: function() {
            publishOwnFeed(false);
        }
    });
}

function videoroom_onPluginAttached() {
    var register = { "request": "join", "room": 1337, "ptype": "publisher", "display": "watney" };
	videoroomPluginHandle.send({"message": register});
}

function videoroom_onMessage(msg, jsep) {
    Janus.debug(msg);
    var event = msg["videoroom"];
    Janus.debug("Event: " + event);
    console.log("Message from the server: " + JSON.stringify(msg));
    if(event != undefined && event != null) {
        if(event === "joined") {
            // Publisher/manager created, negotiate WebRTC and attach to existing feeds, if any
            publisherId = msg["id"];
            mypvtid = msg["private_id"];
            Janus.log("Successfully joined room " + msg["room"] + " with ID " + publisherId);
            publishOwnFeed(true);
            
        } else if(event === "destroyed") {
            // The room has been destroyed
            Janus.warn("The room has been destroyed!");
        } else if(event === "event") {
            if(msg["error"] !== undefined && msg["error"] !== null) {
                Janus.debug("Videoroom error: " + msg["error"]);
            } else if (msg["configured"] === 'ok' && msg["audio_codec"] === 'opus') {
                if (!forwarded) {
                    requestForward();
                }
            }
        }
    }
    if(jsep !== undefined && jsep !== null) {
        Janus.debug("Handling SDP as well...");
        Janus.debug(jsep);
        videoroomPluginHandle.handleRemoteJsep({jsep: jsep});
        Janus.debug("JSEP message: "+  JSON.stringify(msg));
    }
}

function publishOwnFeed(firstTime) {
    const deviceId = getCookie("defaultDevice");
    navigator.mediaDevices.enumerateDevices().then(devices => {
        const device = devices.find(d => d.deviceId === deviceId);
        let constraints;
        if (device) {
            constraints = {video: false, audio: {deviceId}};
        } else {
            constraints = {video: false, audio: true};
        }
        navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            navigator.mediaDevices.enumerateDevices().then(devices => listDevices(devices));

            videoroomPluginHandle.createOffer({
                stream,
                simulcast: false,
                simulcast2: false,
                success: function(jsep) {
                    Janus.debug("Got publisher SDP!");
                    Janus.debug(jsep);
                    var publish = { "request": "publish", "audio": true, "video": false, "data": false, "audiocodec": "opus"};
                    videoroomPluginHandle.send({"message": publish, "jsep": jsep});
                },
                error: function(error) {
                    Janus.error("WebRTC error:", error);
                }
            });
        })
        .catch(reason => {
            console.error("Error getting user media: " + reason);
        });
    });
    
}

function unpublishOwnFeed() {
    var unpublish = { "request": "unpublish" };
	videoroomPluginHandle.send({"message": unpublish});
}

var forwarded = false;
function requestForward() {
    var request = {
        "request": "rtp_forward",
        "room": 1337,
        "publisher_id": publisherId,
        "host": "127.0.0.1",
        "audio_port" : 50000,
        "audio_rtcp_port" : 50001,
        "video_port" : 50002,
        "video_rtcp_port" : 50003,
        "data_port" : 50004,
    };
    videoroomPluginHandle.send({"message": request});
    forwarded = true;
}

function mute() {
    if (videoroomPluginHandle) {
        videoroomPluginHandle.muteAudio();
        $("div#micButton > i").text("mic_off");
    }
}

function unmute() {
    if (videoroomPluginHandle) {
        videoroomPluginHandle.unmuteAudio();
        $("div#micButton > i").text("mic");
    }
}