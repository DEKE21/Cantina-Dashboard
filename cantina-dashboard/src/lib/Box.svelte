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

<div class="box" style="--color:{backgroundColor}" >{title}</div>

<style>
    .box {
        display: flex;
        width: 190px;
        height: 93px;
        border-radius: 12px;
        font-size: 24px;

        word-break: keep-all;

        text-align: center;
        align-content: center;
        justify-content: center;
        align-items: center;
        background-color: var(--color);
    }

</style>
