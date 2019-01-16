var janusConnection;
var streamingPluginHandle;
var forwarderPluginHandle;

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
    })
}

function onJanusConnect() {
    attachStreamingPlugin();
    attachForwarderPlugin();
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

function attachForwarderPlugin() {
    var opaqueId = "forwarder-" + Janus.randomString(12);
    janusConnection.attach({
        plugin: "janus.plugin.rtpforward",
        opaqueId: opaqueId,
        success: function (plugin) {
            forwarderPluginHandle = plugin;
            forwarder_onPluginAttached();
        },
        error: function (error) {
            console.log("Error attaching forwarder plugin: " + error);
        },
        onremotestream: function (stream) {
            //streaming_onRemoteStreamStart(stream);
        },
        onmessage: function (msg, jsep) {
            forwarder_onMessage(msg, jsep);
        }
    });
}

function forwarder_onPluginAttached() {
    
    forwarderPluginHandle.send(
        { 
            "message": 
            {
                "request": "configure",
                "sendipv4": "127.0.0.1",
                "sendport_audio_rtp": 60000,
                "sendport_audio_rtcp": 60001,
                "sendport_video_rtp": 60002,
                "sendport_video_rtcp": 60003,     
            }
        }
    );
    forwarderPluginHandle.send(
        {
            "message":
            {
                "video_enabled": false
            }
        }
    );

    forwarderPluginHandle.createOffer(
        {
            media: {
                audioSend: true,
                audioRecv: false,
                video: false,
                data: false,
            },
            success: function(jsep) {
                forwarderPluginHandle.send(
                    {
                        "message": 
                        {
                            "audio": true,
                            "video": false
                        },
                        "jsep": jsep
                    }
                );
            },
            error: function(error) {
                console.log("Remote offer error: " + error);
            }
        }
    );
    
}

function forwarder_stopStream() {
    if (forwarderPluginHandle) {
        forwarderPluginHandle.hangup();
    }
}

function forwarder_onMessage(msg, jsep) {
    var result = msg["result"];
    if (result && result["status"] && result["status"] === 'stopped') {
        forwarder_stopStream();
    }

    var error = msg["error"];
    if (error) {
        console.log("Remote error: " + error);
        forwarder_stopStream();
    }

    if(jsep !== undefined && jsep !== null) {
        forwarderPluginHandle.handleRemoteJsep({jsep: jsep});
    }
}