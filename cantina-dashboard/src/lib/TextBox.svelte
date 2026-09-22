<script>
    // let title = $state("");
    // let status = $state(false);
    let { title, backgroundColor, w, h } = $props();
</script>

<div class="box" style="--color:{backgroundColor}   ">{title}</div>

<style>
    .box {
        width: auto;
        height: auto;
        border-radius: 10px;

        background-color: var(--color);

        text-align: center;
        font-size: 40px;
    }
</style>
