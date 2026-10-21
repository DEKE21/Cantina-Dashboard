<script lang="js">
	import { onMount } from "svelte";
	import background from "/Falcon_Hyperspace.jpeg";
	import geofence from "./midsouthflightgeofence.json";
	import logo from "/cantinacirclelogo.png";
	import L, { geoJSON } from "leaflet";
	import "leaflet/dist/leaflet.css";

	import Graph from "./lib/Graph.svelte";
	import Box from "./lib/Box.svelte";
	import EstoppedButton from "./lib/EstoppedButton.svelte";
	import TextBox from "./lib/TextBox.svelte";
	import WebSocketClient from "./lib/WebSocketClient.svelte";

	/** @type {HTMLDivElement} **/
	let mapContainer;

	/** @type {import('leaflet').Map} */
	let map;

	let messageBuffer = $state([]);
	let connectionState = $state(false);
	let testState = $state(false);

	let cords = $state([]);
	let polyline;

	let chart1 = $state.raw(null);
	let chart2 = $state.raw(null);
	let altGraph = $state.raw(null);
	let SolarGraph = $state.raw(null);
	let wsClient = $state.raw(null);

	function SendReleaseCommand() {
		if (wsClient) {
			wsClient.SendCommand("CMD RELEASE\n");
		} else {
			console.error("WebSocketClient is not initialized.");
		}
	}
	function SendStowCommand() {
		if (wsClient) {
			wsClient.SendCommand("CMD STOW\n");
		} else {
			console.error("WebSocketClient is not initialized.");
		}
	}
	function SendSolarDeployCommand() {
		if (wsClient) {
			wsClient.SendCommand("CMD DEPLOY\n");
		} else {
			console.error("WebSocketClient is not initialized.");
		}
	}
	function SendSolarRetractCommand() {
		if (wsClient) {
			wsClient.SendCommand("CMD RETRACT\n");
		} else {
			console.error("WebSocketClient is not initialized.");
		}
	}
	function SendTXStartCommand() {
		if (wsClient) {
			wsClient.SendCommand("CMD CX START\n");
		} else {
			console.error("WebSocketClient is not initialized.");
		}
	}
	function SendTXStopCommand() {
		if (wsClient) {
			wsClient.SendCommand("CMD CX STOP\n");
		} else {
			console.error("WebSocketClient is not initialized.");
		}
	}

	function FlipConnectionState() {
		connectionState = !connectionState;
	}

	function FlipState() {
		testState = !testState;
		console.log("FLIP");
	}

	// Telemetry state
	let TEAM_ID = $state("0004");
	let MISSION_TIME = $state([]);
	let PACKET_COUNT = $state(0);
	let STATE = $state("");
	let MECH_STATE = $state(0);

	let ALTITUDE = $state([]);
	let TEMP = $state([]);
	let BATTERY_VOLTAGE = $state([]);
	let SOLAR_1 = $state([]);
	let SOLAR_2 = $state([]);
	let GPS_LATITUDE = $state(0);
	let GPS_LONGITUDE = $state(0);
	let GPS_SATS = $state(0);
	let GYRO_R = $state(0);
	let GYRO_P = $state(0);
	let GYRO_Y = $state(0);
	let ACCEL_X = $state(0);
	let ACCEL_Y = $state(0);
	let ACCEL_Z = $state(0);
	let SOLAR_STATE = $state(0);
	let option = {
		title: {
			text: "Live Data",
			textStyle: { fontWeight: "bold" },
		},
		backgroundColor: "#D0B183",
		tooltip: { trigger: "axis", showDelay: 0, transitionDuration: 0 },
		dataZoom: [
			{
				type: "inside",
				start: 0,
				end: 100,
			},
		],
		xAxis: {
			axisLabel: {
				show: true,
				margin: 8,
				fontSize: 15,
			},
			splitLine: {
				show: true,
				lineStyle: {
					color: "#AA9BAB",
					width: 2,
				},
			},
			type: "category",
			data: [],
			name: "Time (Seconds)",
			nameTextStyle: {
				fontSize: 15,
				fontWeight: "bold",
			},
			nameLocation: "center",
			lineStyle: {
				width: 30,
			},
		},
		yAxis: {
			axisLabel: {
				show: true,
				margin: 8,
				fontSize: 15,
				interval: 0,
			},
			type: "value",
			splitLine: {
				show: true,
				lineStyle: {
					color: "#AA9BAB",
					width: 2,
				},
			},
			name: "Default ()",
			nameTextStyle: {
				fontSize: 15,
				fontWeight: "bold",
			},
			nameLocation: "center",
			lineStyle: {
				width: 30,
			},
		},
		textStyle: { fontWeight: "bold" },
		series: [
			{
				data: [],
				showSymbol: false,
				sampling: "lttb",
				type: "line",
				smooth: true,
				color: "#5580bf",
				itemStyle: {
					borderRadius: [8, 8, 8, 8],
				},
			},
		],
	};

	onMount(() => {
		let initialView = [34.7304, -86.5861];
		map = L.map(mapContainer).setView(initialView, 13);

		let geoGroup = L.featureGroup();

		L.tileLayer(
			"http://localhost:3650/api/maps/m/{z}/{x}/{y}@2x.jpg",
			{},
		).addTo(map);

		function mapper() {
			geofence.features.forEach((element) => {
				let attr = element.attributes;
				let geo = element.geometry.rings;

				let fence = geoJSON({
					type: "Feature",
					properties: { attr },
					geometry: { type: "Polygon", coordinates: geo },
				});

				geoGroup.addLayer(fence);
			});
		}

		polyline = L.polyline(cords, { color: "red" }).addTo(map);
		mapper();
		geoGroup.addTo(map);
		$effect(() => {
			if (cords[0] === 0 && cords[1] === 0) {
				cords.shift();
				return; // Skip updating the map if the first point is [0, 0]
			}
			const ccords = cords;

			if (polyline && L) {
				polyline.setLatLngs(ccords);

				// Pan the camera smoothly to follow the newest point
				if (map && ccords.length > 0) {
					map.panTo(ccords[ccords.length - 1]);
				}
			}
		});
		const dataLoop = setInterval(() => {
			if (messageBuffer.length === 0) return;

			// Splice grabs all pending messages and clears the buffer in one O(1) step
			const currentMessages = messageBuffer.splice(
				0,
				messageBuffer.length,
			);
			let addedCords = false;

			for (let i = 0; i < currentMessages.length; i++) {
				let arg = currentMessages[i];

				if (arg && arg.length >= 14) {
					TEAM_ID = arg[0];
					const packetTime = isNaN(Number(arg[1]))
						? arg[1]
						: Number(arg[1]);

					MISSION_TIME.push(packetTime / 1000);
					PACKET_COUNT = arg[2];
					STATE = arg[3];
					MECH_STATE = arg[4];
					ALTITUDE.push(Number(arg[5]) || 0);
					TEMP.push(Number(arg[6]) || 0);
					BATTERY_VOLTAGE.push(Number(arg[7]) || 0);

					GPS_LATITUDE = arg[8] / 10000000.0;
					GPS_LONGITUDE = arg[9] / 10000000.0;
					GPS_SATS = arg[10];
					GYRO_R = arg[11];
					GYRO_P = arg[12];
					GYRO_Y = arg[13];
					ACCEL_X = arg[14];
					ACCEL_Y = arg[15];
					ACCEL_Z = arg[16];
					SOLAR_STATE = arg[17];

					SOLAR_1.push(Number(arg[18]) || 0);
					SOLAR_2.push(Number(arg[19]) || 0);

					if (GPS_LATITUDE && GPS_LONGITUDE) {
						if (GPS_LATITUDE === 0 && GPS_LONGITUDE === 0) {
							console.warn(
								"Received GPS coordinates are both zero, ignoring.",
							);
							return; // Skip adding this point to the path
						}
						cords.push([GPS_LONGITUDE, GPS_LATITUDE]);
						addedCords = true;
					}
				}
			}

			// Update map only once per tick
			if (addedCords && polyline && map) {
				if (cords[0] === 0 && cords[1] === 0) {
					cords.shift();
				} else {
					polyline.setLatLngs(cords);
					map.setView(cords[cords.length - 1], map.getZoom(), {
						animate: false,
					});
				}
			}
		}, 50);
		return () => {
			map.remove();
			clearInterval(dataLoop);
		};
	});
</script>

<h1 class="banner">
	CANTINA DASHBOARD CANSAT #4
	<img class="logo" alt="logo" src={logo} />
</h1>
<div class="DM">
	<div class="data">
		<div class="app">
			<Graph
				--border-radius="12px"
				titleText="Battery Voltage"
				time={MISSION_TIME}
				liveData={BATTERY_VOLTAGE}
				Units="Voltage (V)"
				UnitSub="V"
				{option}
				bind:chartInstance={chart1}
			/>
		</div>
		<div class="graph-2">
			<Graph
				--border-radius="12px"
				titleText="Temperature"
				Units="Temperature (C°)"
				UnitSub="C°"
				liveData={TEMP}
				time={MISSION_TIME}
				{option}
				bind:chartInstance={chart2}
			/>
		</div>
		<div class="altGraph">
			<Graph
				liveData={ALTITUDE}
				time={MISSION_TIME}
				bind:chartInstance={altGraph}
				--border-radius="12px"
				titleText="Altitude graph"
				Units="Meters (M)"
				UnitSub="M"
				{option}
			/>
		</div>
		<div class="SolarGraph">
			<Graph
				liveData={SOLAR_1}
				liveData2={SOLAR_2}
				time={MISSION_TIME}
				bind:chartInstance={SolarGraph}
				--border-radius="12px"
				titleText="Solar Voltage"
				Units="Voltage (V)"
				UnitSub="V"
				{option}
			/>
		</div>
		<div style="background-color: #f7e9cd;" class="back"></div>
	</div>

	<div class="TextData">
		<div bind:this={mapContainer} class="map"></div>

		<div class="Gryo">
			<TextBox title="DPS" backgroundColor="#A4669C" />

			<TextBox title="X: {GYRO_R}" backgroundColor="#A4669C" />
			<TextBox title="Y: {GYRO_P}" backgroundColor="#A4669C" />
			<TextBox title="Z: {GYRO_Y}" backgroundColor="#A4669C" />
		</div>
		<div class="Acceleration">
			<TextBox title="ACCEL " backgroundColor="#A4669C" />

			<TextBox title="X: {ACCEL_X}" backgroundColor="#A4669C" />
			<TextBox title="Y: {ACCEL_Y}" backgroundColor="#A4669C" />
			<TextBox title="Z: {ACCEL_Z}" backgroundColor="#A4669C" />
		</div>
		<div class="Misc">
			<TextBox
				title="Solar Status: {SOLAR_STATE}"
				backgroundColor="#A4669C"
			/>
			<TextBox title="Flight Status: {STATE}" backgroundColor="#A4669C" />
			<TextBox
				title="Mission Time: {MISSION_TIME.at(-1)}"
				backgroundColor="#A4669C"
			/>
			<div class="dual">
				<TextBox
					title="PKT CNT: {PACKET_COUNT} "
					backgroundColor="#A4669C"
				/>
				<TextBox
					title="Satellites: {GPS_SATS}"
					backgroundColor="#A4669C"
				/>
			</div>
		</div>
		<div class="status">
			<Box title="Active Safety Lock?" status={!connectionState} />

			<Box title="Connected to CanSat?" status={testState} />
		</div>
	</div>
</div>

<div class="ButtonMaster">
	<button class="inputButton" onclick={FlipConnectionState}
		>SAFTEY LOCK</button
	>

	<EstoppedButton
		title="Release Pocket Cube"
		color="#686592"
		ESTOP={connectionState}
		Runnable={SendReleaseCommand}
	/>
	<EstoppedButton
		title="Stow Pocket Cube"
		color="#686592"
		ESTOP={connectionState}
		Runnable={SendStowCommand}
	/>
	<EstoppedButton
		title="Deploy Solar Panels "
		color="#686592"
		ESTOP={connectionState}
		Runnable={SendSolarDeployCommand}
	/><EstoppedButton
		title="Stow Solar Panels "
		color="#686592"
		ESTOP={connectionState}
		Runnable={SendSolarRetractCommand}
	/>
	<EstoppedButton
		title="Enable CX"
		color="#686592"
		ESTOP={connectionState}
		Runnable={SendTXStartCommand}
	/>
	<EstoppedButton
		title="Disable CX"
		color="#686592"
		ESTOP={connectionState}
		Runnable={SendTXStopCommand}
	/>
</div>
<WebSocketClient
	bind:this={wsClient}
	bind:messageBuffer
	bind:connected={testState}
/>

<style>
	:global(html),
	:global(body) {
		margin: 0;
		padding: 1px;
		height: 100vw;
		padding-inline: 20px;
		width: 100%;
		max-width: 1300px;
		margin: 0 auto;
		overflow: hidden;
	}

	.DM {
		display: flex;
		flex-direction: column;
	}
	.banner {
		color: #d0b183;
		font-size: 50px;
		font-family: "Helvetica Black";
		position: fixed;
		top: 0;
		left: 0;
		width: 99.68%;
		height: 10vh;
		border-style: dashed;
		background-color: #86a8d8;
		z-index: 10;
		margin: 0;

		display: flex;
		align-items: center;
		justify-content: center;
	}

	.logo {
		width: 75px;
		height: 75px;

		position: absolute;
		left: 20px;
		top: 50%;
		transform: translateY(-50%);
	}

	.data {
		display: flex;
		flex-direction: row;
		gap: 5px;
		padding: 20px;
		margin-top: 60px;
		height: 460px;
	}

	.map {
		width: 300px;
		height: 298px;
		border-radius: 12px;
		overflow: hidden;
		z-index: 0;
	}

	.ButtonMaster {
		display: flex;
		flex-direction: row;
		gap: 10px;
		width: 930px;
		height: 110px;
		border-radius: 12px;

		transform: translate(322px, -228px);
	}

	.inputButton {
		width: 200px;
		height: 100px;
		border-radius: 12px;
		text-align: center;
		font-size: 24px;
		font-weight: bold;
		background-color: #86a8d8;
	}

	.status {
		display: flex;
		flex-direction: column;
		gap: 5px;
	}

	.TextData {
		display: flex;
		flex-direction: row;
		gap: 2px;

		transform: translate(20px, -125px);
	}
	.Gryo {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.Acceleration,
	.Misc {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.dual {
		display: flex;
		flex-direction: row;
		gap: 2px;
	}
	.back {
		position: fixed;
		top: 0;
		left: 0;
		bottom: 0;
		width: 100vw;
		height: 100vh;
		z-index: -1;
		background-size: cover;
		background-position: center;
		background-repeat: no-repeat;
		pointer-events: none;
	}
</style>
