<script>
    import { onMount } from "svelte";

    let { messageBuffer = $bindable([[]]) } = $props();

    // 1. Move the socket variable to the top level so it can be accessed anywhere
    let socket; 

    // 2. Move SendCommand outside of onMount and add 'export'
    export function SendCommand() {
        console.log("Trying to send command");
        if (socket && socket.readyState === WebSocket.OPEN) {
            console.log("Sending command");
            socket.send("CMD RELEASE\n");
        } else {
            console.error("Socket not open or not initialized");
        }
    }

    onMount(() => {
        const delay = 3000;
        let reconnection = null;

        function ConnectToServer() {
            try {
                socket = new WebSocket("ws://localhost:8001");
                socket.addEventListener("open", Opened);
                socket.addEventListener("close", Closed);
                socket.addEventListener("error", HandleError);
                socket.addEventListener("message", MessageRcv);
            } catch {
                console.log("Failed to connect");
                socket = null;
                Closed();
            }
        }

        function Opened() {
            console.log("Client connection successful");
            if (reconnection) clearTimeout(reconnection);
        }

        function Closed() {
            Cleanup();
            reconnection = setTimeout(() => {
                console.log("Client connection ended, attempting reconnection every 3 seconds");
                ConnectToServer();
            }, delay);
        }

        function MessageRcv(event) {
            let buff = event.data.split(",");
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

        ConnectToServer();

        const pingInterval = setInterval(() => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                // Note: WebSocket.send() only takes one argument. The '0' was invalid.
                socket.send("ping"); 
            }
        }, 1000);

        return () => {
            if (reconnection) clearTimeout(reconnection);
            clearInterval(pingInterval);
            Cleanup();
        };
    });
</script>