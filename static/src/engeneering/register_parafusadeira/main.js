$(document).ready(() => {
    if (document.URL.split("//")[1].split(":")[0] == "127.0.0.1") {
        loadKeyboard()
    }

    const loadParafusadeiras = () => {
        $("#ip").val("")
        $("#marca").val("")
        $("#db_parafusadeira").val("")
        $("#link").val("")
        $("#index_torque").val("")
        $("#index_tempo").val("")
        $.ajax({
            "url": "/parafusadeiras/getAll",
            type: "GET",
            success: (res) => {
                $("#parafusadeiras").empty()
                $("#parafusadeiras").append(
                    $("<option>", { value: 0, text: "Selecione uma parafusadeira..." })
                )
                for (parafusadeira of res.parafusadeiras) {
                    $("#parafusadeiras").append(
                        $("<option>", { value: parafusadeira["_id"], text: parafusadeira["ip"] })
                    )
                }
            }
        })
    }

    loadParafusadeiras()
    $("#parafusadeiras").on("change", function () {
        if (this.value == 0) {
            $("#ip").val("")
            $("#marca").val("")
            $("#db_parafusadeira").val("")
            $("#link").val("")
            $("#index_torque").val("")
            $("#index_tempo").val("")
        } else {
            $.ajax({
                "url": "/parafusadeiras/get/" + this.value,
                type: "GET",
                success: (res) => {
                    $("#ip").val(res.parafusadeira.ip)
                    $("#marca").val(res.parafusadeira.marca)
                    $("#db_parafusadeira").val(res.parafusadeira.db_parafusadeira)
                    $("#link").val(res.parafusadeira.link)
                    $("#index_torque").val(res.parafusadeira.index_torque)
                    $("#index_tempo").val(res.parafusadeira.index_tempo)
                }
            })
        }
    })

    $("#form-parafusadeira").on("submit", (e) => {
        e.preventDefault()

        let ip = $("#ip").val()
        let marca = $("#marca").val()
        let db_parafusadeira = $("#db_parafusadeira").val()
        let link = $("#link").val()
        let index_torque = $("#index_torque").val()
        let index_tempo = $("#index_tempo").val()

        let formData = new FormData()

        formData.append("ip", ip)
        formData.append("marca", marca)
        formData.append("db_parafusadeira", db_parafusadeira)
        formData.append("link", link)
        formData.append("index_torque", index_torque)
        formData.append("index_tempo", index_tempo)

        $.ajax({
            url: "/parafusadeiras/register",
            type: "POST",
            dataType: "json",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: () => {
                Swal.fire("Sucesso!", "", "success")
                loadParafusadeiras()
            },
            error: (e) => {
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

    $("#update_parafusadeira").on("click", () => {
        if ($("#parafusadeiras").val() == 0) return
        let ip = $("#ip").val()
        let marca = $("#marca").val()
        let db_parafusadeira = $("#db_parafusadeira").val()
        let link = $("#link").val()
        let index_torque = $("#index_torque").val()
        let index_tempo = $("#index_tempo").val()

        let formData = new FormData()

        formData.append("ip", ip)
        formData.append("marca", marca)
        formData.append("db_parafusadeira", db_parafusadeira)
        formData.append("link", link)
        formData.append("index_torque", index_torque)
        formData.append("index_tempo", index_tempo)
        formData.append("id", $("#parafusadeiras").val())

        Swal.fire({
            title: 'Tem certeza?',
            text: "Essa ação não pode ser desfeita!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Alterar!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: "/parafusadeiras/update",
                    type: "PUT",
                    processData: false,
                    cache: false,
                    contentType: false,
                    data: formData,
                    success: () => {
                        Swal.fire("Sucesso!", "", "success")
                        loadParafusadeiras()
                    },
                    error: (e) => {
                        console.log(e)
                        Swal.fire(e.responseJSON.msg, "", "error")
                    }
                })
            }
        })

    })

    $("#delete_parafusadeira").on("click", () => {
        if ($("#parafusadeiras").val() == 0) return
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
                    url: "/parafusadeiras/delete/" + $("#parafusadeiras").val(),
                    type: "DELETE",
                    success: () => {
                        Swal.fire("Sucesso!", "", "success")
                        loadParafusadeiras()
                        $("#ip").val("")
                        $("#posto").val("")
                    }
                })
            }
        })
    })

    $("#teste_link").on("click", () => {
        let link = $("#link").val()
        if (!link) return Swal.fire("Digite o link!", "", "info")

        let formData = new FormData()

        formData.append("link", link)

        $.ajax({
            url: "/testeLink",
            type: "POST",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: res => {
                let array = res.index
                let array_string = `
                <div class="item-list"> 
                    Index
                </div>
                <div class="item-list"> 
                    Valor
                </div>
                `
                Array.from(array).forEach((value, i) => {
                    array_string += `
                    <div class="item-list"> 
                        ${i}
                    </div>
                    <div class="item-list"> 
                       ${value}
                    </div>
                    `
                })

                array_string = `
                    <div class="list-container"> ${array_string} </div>
                 `

                Swal.fire({
                    html: array_string,
                    showCancelButton: false
                })

            },
            error: (e) => {
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

})
