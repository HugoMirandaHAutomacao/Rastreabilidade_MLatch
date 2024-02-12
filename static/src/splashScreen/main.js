let interval = setInterval(() => {
    $.ajax({
        url: "/getProperties",
        cache: false,
        success: (res) => {
            if (res.properties.inited) {
                clearInterval(interval)
                document.location.href = "/"
            }
        }, error: (e) => {
            console.log("not open")
        }
    })
}, 1000)