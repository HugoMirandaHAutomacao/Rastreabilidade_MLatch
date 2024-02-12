$(document).ready(() => {    
    if (document.URL.split("//")[1].split(":")[0] == "127.0.0.1") {
        loadKeyboard()
    }
    $.ajax({
        "url": "/clp/get",
        type: "GET",
        success: (res) => {
            $("#ip").val(res.plc.ip)
            $("#rack").val(res.plc.rack)
            $("#slot").val(res.plc.slot)
            $("#descricao").val(res.plc.desc)
            $("#db").val(res.plc.db)
        }
    })

    $("#form-clp").on("submit", (e) => {
        e.preventDefault()

        let ip = $("#ip").val()
        let rack = $("#rack").val()
        let slot = $("#slot").val()
        let desc = $("#descricao").val()
        let db = $("#db").val()

        let formData = new FormData()

        formData.append("ip", ip)
        formData.append("rack", rack)
        formData.append("slot", slot)
        formData.append("desc", desc)
        formData.append("db", db)

        $.ajax({
            url: "/clp/update",
            type: "PUT",
            dataType: "json",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: () => {
                Swal.fire("Sucesso!", "", "success")
            },
            error: (e) => {
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })

    })
})
