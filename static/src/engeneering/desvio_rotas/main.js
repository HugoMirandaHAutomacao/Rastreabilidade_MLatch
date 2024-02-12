$(document).ready(() => {

    if (document.URL.split("//")[1].split(":")[0] == "127.0.0.1") {
        loadKeyboard()
    }
    const loadRotas = () => {
        $.ajax({
            "url": "/rotas/getAll",
            type: "GET",
            success: (res) => {
                $("#rotas").empty()
                $("#rotas").append(
                    $("<option>", { value: 0, text: "Selecione um desvio de rota..." })
                )
                for (rota of res.rotas) {
                    $("#rotas").append(
                        $("<option>", { value: rota["_id"], text: rota["codigo"] })
                    )
                }
            }
        })
    }
    loadRotas()
    $("#rotas").on("change", function () {
        if (this.value == 0) {
            $("#ip").val("")
            $("#codigo").val("")
        } else {
            $.ajax({
                "url": "/rotas/get/" + this.value,
                type: "GET",
                success: (res) => {
                    $("#ip").val(res.rotas.ip)
                    $("#codigo").val(res.rotas.codigo)
                }
            })
        }
    })

    $("#form-rotas").on("submit", (e) => {
        e.preventDefault()

        let ip = $("#ip").val()
        let cod = $("#codigo").val()

        let formData = new FormData()

        formData.append("ip", ip)
        formData.append("codigo", cod)

        $.ajax({
            url: "/rotas/register",
            type: "POST",
            dataType: "json",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: () => {
                Swal.fire("Sucesso!", "", "success").then(() => {
                    $("#ip").val("")
                    $("#codigo").val("")
                })
                loadRotas()
            },
            error: (e) => {
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

    $("#update_rota").on("click", () => {
        if ($("#rotas").val() == 0) return
        let ip = $("#ip").val()
        let codigo = $("#codigo").val()

        let formData = new FormData()

        formData.append("ip", ip)
        formData.append("codigo", codigo)
        formData.append("id", $("#rotas").val())

        $.ajax({
            url: "/rotas/update",
            type: "PUT",
            dataType: "json",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: () => {
                Swal.fire("Sucesso!", "", "success")
                $("#ip").val("")
                $("#codigo").val("")
                loadRotas()
            },
            error: (e) => {
                console.log(e)
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

    $("#delete_rota").on("click", () => {
        if ($("#rotas").val() == 0) return
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
                    url: "/rotas/delete/" + $("#rotas").val(),
                    type: "DELETE",
                    success: () => {
                        Swal.fire("Sucesso!", "", "success")
                        loadRotas()
                        $("#ip").val("")
                        $("#codigo").val("")
                    }
                })
            }
        })
    })
})
