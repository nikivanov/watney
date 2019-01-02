var janusConnection;
var pluginHandle;

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
            onJanusConnect(janusConnection);
        },
        error: function (error) {
            alert("Janus server error: " + error);
        },
        destroyed: function () {

        }
    })
}

function onJanusConnect() {
    var opaqueId = "streamingtest-" + Janus.randomString(12);
    janusConnection.attach({
        plugin: "janus.plugin.streaming",
        opaqueId: opaqueId,
        success: function (plugin) {
            pluginHandle = plugin;
            onPluginAttached();
        },
        error: function (error) {
            console.log("Error attaching plugin: " + error);
        },
        onremotestream: function (stream) {
            onRemoteStreamStart(stream);
        },
        onmessage: function (msg, jsep) {
            onRemoteMessage(msg, jsep);
        }
    });
}

function onRemoteStreamStart(stream) {
    $("#vid").bind("playing", function () {
        console.log("I'm playing now!");
    });
    var vidEl = $("#vid").get(0);
    Janus.attachMediaStream(vidEl, stream);

}

function onPluginAttached() {
    // Watney HD stream is id 10
    var body = { "request": "watch", id: 10 };
    pluginHandle.send({ "message": body });
}

function onRemoteMessage(msg, jsep) {
    var result = msg["result"];
    if (result && result["status"] && result["status"] === 'stopped') {
        stopStream();
    }

    var error = msg["error"];
    if (error) {
        console.log("Remote error: " + error);
        stopStream();
    }

    if (jsep) {
        pluginHandle.createAnswer({
            jsep: jsep,
            media: {
                audioSend: false,
                videoSend: false,
                data: true,
            },
            success: function (jsep) {
                var body = { "request": "start" };
                pluginHandle.send({ "message": body, "jsep": jsep });
            },
            error: function (error) {
                console.log("Remote offer error: " + error);
            }
        });
    }
}

function stopStream() {
    if (pluginHandle) {
        var body = { "request": "stop" };
        pluginHandle.send({ "message": body });
        pluginHandle.hangup();
    }
}