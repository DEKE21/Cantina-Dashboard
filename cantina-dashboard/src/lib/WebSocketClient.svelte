<script>
    import { onMount } from "svelte";

    // 1. Default to an empty array [] instead of [[]]
    let { messageBuffer = $bindable([]), connected = $bindable(false) } =
        $props();

    let socket = null;

    export function SendCommand(cmd) {
        console.log("Trying to send command:", cmd.trim());
        if (socket && socket.readyState === WebSocket.OPEN) {
            console.log("Sending command");
            socket.send(cmd);
        } else {
            console.error("Socket not open or not initialized");
        }
    }

    onMount(() => {
        const delay = 3000;
        let reconnection = null;
        let isDestroyed = false;

        function ConnectToServer() {
            if (isDestroyed) return;
            Cleanup();

            try {
                socket = new WebSocket("ws://localhost:8001");
                socket.addEventListener("open", Opened);
                socket.addEventListener("close", Closed);
                socket.addEventListener("error", HandleError);
                socket.addEventListener("message", MessageRcv);
            } catch (err) {
                console.error("Failed to connect:", err);
                Closed();
            }
        }

        function Opened() {
            console.log("Client connection successful");
            if (reconnection) {
                clearTimeout(reconnection);
                reconnection = null;
            }
        }

        function Closed() {
            connected = false;
            Cleanup();
            if (!isDestroyed && !reconnection) {
                reconnection = setTimeout(() => {
                    reconnection = null;
                    console.log(
                        "Client connection ended, attempting reconnection...",
                    );
                    ConnectToServer();
                }, delay);
            }
        }

        function MessageRcv(event) {
            if (typeof event.data !== "string") return;

            const raw = event.data.trim();
            connected = true;
            // Ignore empty messages or ping/pong heartbeats
            if (!raw || raw === "ping" || raw === "pong") return;

            const buff = raw.split(",");
            // Only push valid telemetry packets
            if (buff.length >= 14) {
                //messageBuffer.push(buff);

                messageBuffer = [...messageBuffer, buff];
            } else {
                console.warn("Ignored malformed/non-telemetry packet:", raw);
            }
        }

        function Cleanup() {
            if (socket) {
                socket.removeEventListener("open", Opened);
                socket.removeEventListener("close", Closed);
                socket.removeEventListener("error", HandleError);
                socket.removeEventListener("message", MessageRcv);
                if (
                    socket.readyState === WebSocket.OPEN ||
                    socket.readyState === WebSocket.CONNECTING
                ) {
                    socket.close();
                }
                socket = null;
            }
        }   

        function HandleError() {
            console.error("WebSocket encountered an error");
        }

        ConnectToServer();

        const pingInterval = setInterval(() => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send("ping");
            }
        }, 1000);

        return () => {
            isDestroyed = true;
            if (reconnection) clearTimeout(reconnection);
            clearInterval(pingInterval);
            Cleanup();
        };
    });
</script>
