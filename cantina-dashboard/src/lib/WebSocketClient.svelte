<script>
    import { Handler } from "leaflet";
    import { onMount } from "svelte";
    import { derived } from "svelte/store";

    let { messageBuffer = $bindable([[]]) } = $props();

    onMount(() => {
        const DeploySolarCMD = "CMD";
        const RetractSolarCMD = "CMD, M, 1";
        let socket;
        const delay = 3000;
        let reconnection = null;

        function ConnectToServer() {
            try {
                socket = new WebSocket("ws://localhost:8001");
            } catch {
                console.log("Failed to reconnect ");
                socket = null;
                Closed();
            }
            socket.addEventListener("open", Opened);
            socket.addEventListener("close", Closed);
            socket.addEventListener("error", HandleError);
            socket.addEventListener("message", MessageRcv);
        }
        //wait 3 seconds
        function Opened() {
            console.log("Client connection successful");
            if (reconnection) clearTimeout(reconnection);
        }
        function Closed() {
            Cleanup();
            reconnection = setTimeout(() => {
                console.log(
                    "Client connection ended, attemping reconnection every 3 seconds",
                );
                try {
                    ConnectToServer();
                } catch {
                    console.log("Failed to reconnect ");
                    socket = null;
                }
            }, delay);
        }
        function MessageRcv(event) {
            let ar = [];
            let x = event.data;
            let buff = x.split(",");
            // console.log('buf', buff);
            messageBuffer.push(buff);
        }
        function Cleanup() {
            if (socket) {
                socket = null;
            }
        }

        function HandleError(event) {
            console.error("WebSocket encountered an error");
        }

        function ListenForMessage() {}

        ConnectToServer();
        setInterval(() => {
            if (socket && socket.readyState == WebSocket.OPEN) {
                socket.send("ping", 0);
            }
        }, 1000);
        return () => {
            if (reconnection) clearTimeout(reconnection);
            Cleanup();
        };
    });
</script>
