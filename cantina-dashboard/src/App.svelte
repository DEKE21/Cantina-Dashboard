<script lang="js">
	import { onMount } from "svelte";
	import background from "/Falcon_Hyperspace.jpeg";
	import geofence from "./midsouthflightgeofence.json";
	import logo from "/croppedcantinalogo.png";
	import L, {
		geoJSON,
		Marker,
		polygon,
		popup,
		DomEvent,
		Layer,
		Polyline,
	} from "leaflet";
	import "leaflet/dist/leaflet.css";

	import * as echarts from "echarts";
	import { init, use } from "echarts/core";
	import { BarChart } from "echarts/charts";
	import { GridComponent, TitleComponent } from "echarts/components";
	import { CanvasRenderer } from "echarts/renderers";

	import "./lib/AltitudeGraph.svelte";
	import Graph from "./lib/Graph.svelte";
	import Box from "./lib/Box.svelte";
	import AltitudeGraph from "./lib/AltitudeGraph.svelte";
	import EstoppedButton from "./lib/EstoppedButton.svelte";
	import TextBox from "./lib/TextBox.svelte";
	import WebSocketClient from "./lib/WebSocketClient.svelte";

	// import tailwindcss from '@tailwindcss/vite'
	/** @type {HTMLDivElement} **/
	let mapContainer;

	/** @type {import('leaflet').Map} */
	let map;
	let chart = $state();
	let chartDom;
	let chartInstance;
	let updateInterval;
	let time = [0];
	let dataData = [0];
	let messageBuffer = $state([[0]]);

	let connectionState = $state(false);
	let testState = $state(false);
	let cords = [
		[34.670843, -86.682593],
		[34.748023, -86.554158],
		[34.821717, -86.42878],
	];
	let d = $state([]);
	let chart2 = $state();
	let altGraph = $state();
	let SolarGraph = $state();
	let altitudeData = $state([[]]);
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
			type: "value",
			data: time,
			name: "Time (Seconds)",
			nameTextStyle: {
				fontSize: 15, // Set font size in pixels (default is 12)
				fontWeight: "bold", // Optional: 'normal', 'bold', 'bolder', or 'lighter'
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
				fontSize: 15, // Font size
				interval: 0, // Force show all labels
			},
			type: "value",
			splitLine: {
				show: true,
				lineStyle: {
					color: "#AA9BAB",
					width: 2,
				},
			},
			lineStyle: {
				width: 10,
			},
			name: "Default ()",
			nameTextStyle: {
				fontSize: 15, // Set font size in pixels (default is 12)
				fontWeight: "bold", // Optional: 'normal', 'bold', 'bolder', or 'lighter'
			},
			nameLocation: "center",
			lineStyle: {
				width: 30,
			},
		},

		textStyle: { fontWeight: "bold" }, //color: "rgb(211,225,220)"
		axis: {
			lineStyle: { width: 20, fontWeight: "bold" },
		},
		series: [
			{
				data: dataData,
				showSymbol: false, // Speeds up rendering significantly by omitting point dots
				sampling: "lttb",
				type: "line",
				smooth: true,
				color: "#5580bf",
				itemStyle: {
					borderRadius: [8, 8, 8, 8], // Rounds top-left and top-right corners
				},
			},
		],
	};

	let counter = $state(0);

	$effect(() => {
		dataData.shift();
		dataData.push(counter);
	});
	function FlipConnectionState() {
		if (connectionState) {
			connectionState = false;
		} else {
			connectionState = true;
		}
	}
	function FlipState() {
		if (testState) {
			testState = false;
		} else {
			testState = true;
		}
		console.log("FLIP");
	}

	let TEAM_ID = $state.raw("0004");
	let MISSION_TIME = $state.raw(0);
	let PACKET_COUNT = $state.raw(0);
	let STATE = $state.raw("");
	let MECH_STATE = $state.raw(0);
	let ALTITUDE = $state([]);
	let TEMP = $state([]);
	let BATTERY_VOLTAGE = $state([]);
	let GPS_LATITUDE = $state.raw(0);
	let GPS_LONGITUDE = $state.raw(0);
	let GPS_SATS = $state.raw(0);
	let GYRO_R = $state.raw(0);
	let GYRO_P = $state.raw(0);
	let GYRO_Y = $state.raw(0);











	let bigOption = {
		grid:[],
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
			type: "value",
			data: time,
			name: "Time (Seconds)",
			nameTextStyle: {
				fontSize: 15, // Set font size in pixels (default is 12)
				fontWeight: "bold", // Optional: 'normal', 'bold', 'bolder', or 'lighter'
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
				fontSize: 15, // Font size
				interval: 0, // Force show all labels
			},
			type: "value",
			splitLine: {
				show: true,
				lineStyle: {
					color: "#AA9BAB",
					width: 2,
				},
			},
			lineStyle: {
				width: 10,
			},
			name: "Default ()",
			nameTextStyle: {
				fontSize: 15, // Set font size in pixels (default is 12)
				fontWeight: "bold", // Optional: 'normal', 'bold', 'bolder', or 'lighter'
			},
			nameLocation: "center",
			lineStyle: {
				width: 30,
			},
		},

		textStyle: { fontWeight: "bold" }, //color: "rgb(211,225,220)"
		axis: {
			lineStyle: { width: 20, fontWeight: "bold" },
		},
		series: [
			{
				data: dataData,
				showSymbol: false, // Speeds up rendering significantly by omitting point dots
				sampling: "lttb",
				type: "line",
				smooth: true,
				color: "#5580bf",
				itemStyle: {
					borderRadius: [8, 8, 8, 8], // Rounds top-left and top-right corners
				},
			},
		],
	};












	onMount(() => {
		//chart = echarts.init(chartDom);

		use([BarChart, GridComponent, CanvasRenderer, TitleComponent]);

		//chart.setOption(option);
		/*
		$effect(() => {
			if (messageBuffer) {
				console.log("p", messageBuffer);

				TEAM_ID = 4;
				MISSION_TIME = messageBuffer[-1][1];
				PACKET_COUNT = messageBuffer.at(-1)[2];
				STATE = messageBuffer.at(-1)[3];
				MECH_STATE = messageBuffer.at(-1)[4];
				ALTITUDE.push(parseInt(messageBuffer.at(-1)[5]));
				TEMP.push(parseInt(messageBuffer.at(-1)[6]));
				BATTERY_VOLTAGE.push(messageBuffer.at(-1)[7]);
				GPS_LATITUDE = messageBuffer.at(-1)[8];
				GPS_LONGITUDE = messageBuffer.at(-1)[9];
				GPS_SATS = messageBuffer.at(-1)[10];
				GYRO_R = messageBuffer.at(-1)[11];
				GYRO_P = messageBuffer.at(-1)[12];
				GYRO_Y = messageBuffer.at(-1)[13];
				messageBuffer.shift();
			}
		});*/
		function UpdateTelemetry() {}
		let initialView = [34.7304, -86.5861];

		map = L.map(mapContainer).setView(initialView, 13);

		let geoGroup = L.featureGroup();

		L.tileLayer(
			"https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
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
		L.polyline(cords, { color: "red" }).addTo(map);
		mapper();
		geoGroup.addTo(map);
		let currentTime = $state(0);
		let alt = $state(0);
		let updateInterval = setInterval(() => {
			console.log("bufferm");
			if (messageBuffer.length > 0) {
				let arg = messageBuffer.pop();
			
				console.log("p", messageBuffer);

				TEAM_ID = 4;
				MISSION_TIME = parseInt(arg[1]);
 
				//messageBuffer[-1][1];
				PACKET_COUNT = arg[2];
				STATE = arg[3];
				MECH_STATE = arg[4];
				ALTITUDE.push(parseInt(arg[5]));
				TEMP.push(parseInt(arg[6]));
				BATTERY_VOLTAGE.push(arg[7]);
				GPS_LATITUDE = arg[8];
				GPS_LONGITUDE = arg[9];
				GPS_SATS = arg[10];
				GYRO_R = arg[11];
				GYRO_P = arg[12];
				GYRO_Y = arg[13];
			}
			currentTime += 0.25;
			const randomValue = Math.floor(Math.random() * 100);
			d.push(randomValue);
			altitudeData.push([currentTime, alt]);
			alt += 5;

			time.push(currentTime);
		}, 250);

		return () => {
			map.remove();
			clearInterval(updateInterval);
			resizeObserver.disconnect();
		};
	});
</script>

<WebSocketClient {messageBuffer} />
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
				liveData={d}
				Units="Voltage (V)"
				UnitSub="V"
				{option}
			/>
		</div>
		<div class="graph-2">
			<Graph
				--border-radius="12px"
				titleText="Temperature"
				Units="Temperature (C&deg;)"
				UnitSub="C&deg;"
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
				liveData={d}
				time={MISSION_TIME}
				bind:chartInstance={SolarGraph}
				--border-radius="12px"
				titleText="Solar graph"
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
			<TextBox title="X-DPS: 1.000" backgroundColor="#A4669C" />
			<TextBox title="Y-DPS: 1.000" backgroundColor="#A4669C" />
			<TextBox title="Z-DPS: 1.000" backgroundColor="#A4669C" />
		</div>
		<div class="Acceleration">
			<TextBox title="X-Acceleration: 1.000" backgroundColor="#A4669C" />
			<TextBox title="Y-Acceleration: 1.000" backgroundColor="#A4669C" />
			<TextBox title="Z-Acceleration: 1.000" backgroundColor="#A4669C" />
		</div>
		<div class="Misc">
			<TextBox title="Sats: 3" backgroundColor="#A4669C" />
			<TextBox
				title="Packet count: {PACKET_COUNT}"
				backgroundColor="#A4669C"
			/>
			<TextBox title="Solar Status: DEPLOYED" backgroundColor="#A4669C" />
			<TextBox title="Flight Status: {STATE}" backgroundColor="#A4669C" />
		</div>
	</div>
</div>
<div class="time">Mission Time: 4:44.00</div>
<div class="status">
	<Box title="Active Safety Lock?" status={!connectionState} />

	<Box title="Connected to CanSat?" status={testState} />
</div>
<div class="ButtonMaster">
	<button class="inputButton" onclick={FlipConnectionState}
		>SAFTEY LOCK</button
	>

	<EstoppedButton
		title="Release Pocket Cube"
		color="#686592"
		ESTOP={connectionState}
		Runnable={FlipState}
	/>
	<EstoppedButton
		title="Deploy Solar Panels "
		color="#686592"
		ESTOP={connectionState}
		Runnable={FlipState}
	/>
</div>

<style>
	html,
	body {
		margin: 0;
		padding: 0;
		width: 100vw;
		height: 100vh;
		overflow: hidden;
	}

	* {
		box-sizing: border-box;
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
		width: 100%;
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
		width: 110px;
		height: 80px;

		position: absolute;
		left: 20px;
		top: 50%;
		transform: translateY(-50%);
	}

	.data {
		display: flex;
		flex-direction: row;
		gap: 15px;
		padding: 20px;
		margin-top: 10vh;
		height: 68vh;
	}

	.map {
		width: 300px;
		height: 300px;
		border-radius: 12px;
		overflow: hidden;
		z-index: 0;
	}

	.time {
		transform: translate(322px, -304px);
		width: 585px;
		background-color: #a4669c;
		border-radius: 10px;
		font-size: 40px;
	}
	.ButtonMaster {
		display: flex;
		flex-direction: row;
		gap: 10px;

		transform: translate(1015px, -400px);
	}

	.inputButton {
		width: 100px;
		height: 100px;
		border-radius: 12px;
		background-color: #86a8d8;
	}

	.status {
		display: flex;
		flex-direction: row;
		gap: 10px;
		flex-grow: 1;
		transform: translate(325px, -300px);
	}

	.TextData {
		display: flex;
		flex-direction: row;
		gap: 2px;

		transform: translate(20px, -50%);
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
	.back {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
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
