$(document).ready(() => {

    const loadips = () => {
        $.ajax({
            "url": "/ips/getAll",
            type: "GET",
            success: (res) => {
                $("#ips").empty()
                $("#ips").append(
                    $("<option>", { value: 0, text: "Selecione um ip..." })
                )
                for (ip of res.ips) {
                    $("#ips").append(
                        $("<option>", { value: ip["_id"], text: ip["posto"] })
                    )
                }
            }
        })
    }
    loadips()
    $("#ips").on("change", function () {
        if (this.value == 0) {
            $("#ip").val("")
            $("#posto").val("")
        } else {
            $.ajax({
                "url": "/ips/get/" + this.value,
                type: "GET",
                success: (res) => {
                    $("#ip").val(res.ips.ip)
                    $("#posto").val(res.ips.posto)
                }
            })
        }
    })

    $("#form-ips").on("submit", (e) => {
        e.preventDefault()

        let ip = $("#ip").val()
        let cod = $("#posto").val()

        let formData = new FormData()

        formData.append("ip", ip)
        formData.append("posto", cod)

        $.ajax({
            url: "/ips/register",
            type: "POST",
            dataType: "json",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: () => {
                Swal.fire("Sucesso!", "", "success").then(() => {
                    $("#ip").val("")
                    $("#posto").val("")
                })
                loadips()
            },
            error: (e) => {
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

    $("#update_ip").on("click", () => {
        if ($("#ips").val() == 0) return
        let ip = $("#ip").val()
        let posto = $("#posto").val()

        let formData = new FormData()

        formData.append("ip", ip)
        formData.append("posto", posto)
        formData.append("id", $("#ips").val())

        $.ajax({
            url: "/ips/update",
            type: "PUT",
            dataType: "json",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: () => {
                Swal.fire("Sucesso!", "", "success")
                $("#ip").val("")
                $("#posto").val("")
                loadips()
            },
            error: (e) => {
                console.log(e)
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

    $("#delete_ip").on("click", () => {
        if ($("#ips").val() == 0) return
        Swal.fire({
            title: 'Tem certeza?',
            text: "Essa ação não pode ser desfeita!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Deletar!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: "/ips/delete/" + $("#ips").val(),
                    type: "DELETE",
                    success: () => {
                        Swal.fire("Sucesso!", "", "success")
                        loadips()
                        $("#ip").val("")
                        $("#posto").val("")
                    }
                })
            }
        })
    })
})
