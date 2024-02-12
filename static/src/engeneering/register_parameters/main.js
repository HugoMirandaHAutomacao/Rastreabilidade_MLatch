$(document).ready(() => {

    if (document.URL.split("//")[1].split(":")[0] == "127.0.0.1") {
        loadKeyboard()
    }
    const loadParams = () => {
        $.ajax({
            "url": "/param/getAll",
            type: "GET",
            success: (res) => {
                $("#params").empty()
                $("#params").append(
                    $("<option>", { value: 0, text: "Selecione um parâmetro..." })
                )
                for (param of res.params) {
                    $("#params").append(
                        $("<option>", { value: param["_id"], text: param["param"] })
                    )
                }
            }
        })
    }
loadParams()
    $("#params").on("change", function () {
        if (this.value == 0) {
            $("#param").val("")
            $("#memoria").val("")
            $("#plcs").val(0)
        } else {
            $.ajax({
                "url": "/param/get/" + this.value,
                type: "GET",
                success: (res) => {
                    $("#param").val(res.param.param)
                    $("#memoria").val(res.param.memoria)
                }
            })
        }
    })

    $("#form-param").on("submit", (e) => {
        e.preventDefault()

        if ($("#plcs").val() == 0) return Swal.fire("Nenhum CLP selecionado!", "", "info")

        let param = $("#param").val()
        let memoria = $("#memoria").val()

        let formData = new FormData()

        formData.append("param", param)
        formData.append("memoria", memoria)

        $.ajax({
            url: "/param/register",
            type: "POST",
            dataType: "json",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: () => {
                Swal.fire("Sucesso!", "", "success").then(() => {
                    $("#param").val("")
                    $("#memoria").val("")
                    $("#plcs").val(0)
                })
                loadParams()
            },
            error: (e) => {
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

    $("#update_param").on("click", () => {
        if ($("#params").val() == 0) return
        let param = $("#param").val()
        let memoria = $("#memoria").val()
        let plc = $("#plcs").val()

        let formData = new FormData()

        formData.append("param", param)
        formData.append("memoria", memoria)
        formData.append("id", $("#params").val())

        $.ajax({
            url: "/param/update",
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
                console.log(e)
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

    $("#delete_param").on("click", () => {
        if ($("#params").val() == 0) return
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
                    url: "/param/delete/" + $("#params").val(),
                    type: "DELETE",
                    success: () => {
                        Swal.fire("Sucesso!", "", "success")
                        loadParams()
                        $("#param").val("")
                        $("#memoria").val("")
                        $("#plcs").val(0)
                    }
                })
            }
        })
    })
})
