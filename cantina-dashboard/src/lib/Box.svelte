<script>
    // let title = $state("");
    // let status = $state(false);
    let { title, status } = $props();
    let backgroundColor = $state("#ff0000");
    $effect(() => {
        if (status == true) {
            backgroundColor = "#32fd04";
        } else {
            backgroundColor = "#ff0000";
        }
    });
</script>

<div class="box" style="--color:{backgroundColor}">{title}</div>

<style>
    .box {
        width: 100px;
        height: 100px;
        border-radius: 5px;
        font-size: 20px;
        text-align: center;
        justify-content: center;
        align-items: center; 
        
        background-color: var(--color);
    }
</style>
