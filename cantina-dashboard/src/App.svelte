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
	let connectionState = $state(false);
	let testState = $state(false);
	let cords = [
		[34.670843, -86.682593],
		[34.748023, -86.554158],
		[34.821717, -86.42878],
	];
	let d = $state([[]]);
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
	onMount(() => {
		//chart = echarts.init(chartDom);

		use([BarChart, GridComponent, CanvasRenderer, TitleComponent]);

		//chart.setOption(option);

		let telemetry = $state({
			TEAM_ID: "0004",
			MISSION_TIME: 0.0,
			PACKET_COUNT: 0,
			STATE: "k",
			MECH_STATE: "k",
			ALTITUDE: 0,
			TEMP: 0,
			BATTERY_VOLTAGE: 0,
			GPS_LATITUDE: 0,
			GPS_LONGITUDE: 0,
			GPS_SATS: 0,
			GYRO_R: 0,
			GYRO_P: 0,
			GYRO_Y: 0,
		});

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
		updateInterval = setInterval(() => {
			currentTime += 0.25;
			const randomValue = Math.floor(Math.random() * 100);
			d.push([currentTime, randomValue]);
			altitudeData.push([currentTime, alt]);
			alt += 5;

			time.push(currentTime);
			chart.setOption({
				xAxis: [{ data: currentTime }],
				series: [{ data: d }],
			});
		}, 250);
		//const resizeObserver = new ResizeObserver(() => chart?.resize());
		//resizeObserver.observe(chartDom);

		//echarts.connect([chart, chart2, altGraph]);
		return () => {
			map.remove();
			clearInterval(updateInterval);
			resizeObserver.disconnect();
			//chart?.dispose();
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
				liveData={d}
				{option}
				bind:chartInstance={chart2}
			/>
		</div>
		<div class="altGraph">
			<Graph
				liveData={altitudeData}
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
			<TextBox title="Packet count: 10154" backgroundColor="#A4669C" />
			<TextBox title="Solar Status: DEPLOYED" backgroundColor="#A4669C" />
			<TextBox title="Flight Status: DESCENT" backgroundColor="#A4669C" />
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
	/* 1. Header Fix: Pinned to edges, flex-aligned content */
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

		/* Flexbox layout to center the main text */
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
		width: 100%;
		
	}

	.map {
		width: 300px;
		height: 300px;
		border-radius: 12px;
		overflow: hidden;
		z-index: 0;
	}

	.app,
	.graph-2,
	.altGraph {
		flex: 1;
		height: 100%;
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
