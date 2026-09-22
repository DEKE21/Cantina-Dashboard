<script>
    // let title = $state("");
    // let status = $state(false);
    let { title, status } = $props();
    let backgroundColor = $state("#ff0000");
    $effect(() => {
        if (status == true) {
            backgroundColor = "#99FF99";
        } else {
            backgroundColor = "#FD4835";
        }
    });
</script>

<div class="box" style="--color:{backgroundColor}">
    <div class="textbox">{title}</div>
</div>

<style>
    .box {
        display: flex;
        width: 100px;
        height: 100px;
        border-radius: 5px;

        background-color: var(--color);
    }
    .textbox {
        gap: 10px;
        width: 90px;
        height: 90px;
        font-size: 20px;

        word-break: keep-all;
        width: 1ch;

        text-align: center;
        align-content: center;
        justify-content: center;
        align-items: center;
    }
</style>
