$(document).ready(() => {

    if (document.URL.split("//")[1].split(":")[0] == "127.0.0.1") {
        loadKeyboard()
    }
    const loadUsers = () => {
        $.ajax({
            "url": "/users/getAll",
            type: "GET",
            success: (res) => {
                $("#users").empty()
                $("#users").append(
                    $("<option>", { value: 0, text: "Selecione um usuário..." })
                )
                for (user of res.users) {
                    $("#users").append(
                        $("<option>", { value: user["_id"], text: user["nome"] })
                    )
                }
            }
        })
    }

    loadUsers()

    $("#users").on("change", function () {
        if (this.value == 0) {
            $("#nome").val("")
            $("#rfid").val("")
            $("#password").val("")
            $("#chapa_input").val("")
            $("[permission]").each((i, el) => {
                el.checked = false
            })
        } else {
            $.ajax({
                "url": "/users/get/" + this.value,
                type: "GET",
                success: (res) => {
                    $("#nome").val(res.user.nome)
                    $("#rfid").val(res.user.rfid)
                    $("#password").val("")
                    $("#chapa_input").val(res.user.chapa)
                    Object.entries(res.user.permissions).forEach(([key, val]) => {
                        $(`[permission=${key}]`)[0].checked = val
                    })
                }
            })
        }
    })

    $("#form-user").on("submit", (e) => {
        e.preventDefault()

        let nome = $("#nome").val()
        let rfid = $("#rfid").val()
        let chapa = $("#chapa_input").val()
        let password = $("#password").val()
        let formData = new FormData()

        let permissions = {}

        $("[permission]").each((i, el) => {
            permissions[el.getAttribute("permission")] = el.checked
        })

        formData.append("nome", nome)
        formData.append("rfid", rfid)
        formData.append("chapa", chapa)
        formData.append("password", password)
        formData.append("permissions", JSON.stringify(permissions))

        $.ajax({
            url: "/users/register",
            type: "POST",
            dataType: "json",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: () => {
                Swal.fire("Sucesso!", "", "success").then(() => {
                    $("#nome").val("")
                    $("#rfid").val("")
                    $("#password").val("")
                    $("#chapa_input").val("")
                    $("[permission]").each((i, el) => {
                        el.checked = false
                    })
                })
                loadUsers()
            },
            error: (e) => {
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

    $("#update_user").on("click", () => {
        if ($("#users").val() == 0) return
        let nome = $("#nome").val()
        let rfid = $("#rfid").val()
        let chapa = $("#chapa_input").val()
        let password = $("#password").val()
        let permissions = {}

        $("[permission]").each((i, el) => {
            permissions[el.getAttribute("permission")] = el.checked
        })

        let formData = new FormData()

        formData.append("nome", nome)
        formData.append("rfid", rfid)
        formData.append("chapa", chapa)
        formData.append("password", password)
        formData.append("permissions", JSON.stringify(permissions))
        formData.append("id", $("#users").val())

        $.ajax({
            url: "/users/update",
            type: "PUT",
            dataType: "json",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: () => {
                Swal.fire("Sucesso!", "", "success")
                loadUsers()
                $("#nome").val("")
                $("#rfid").val("")
                $("#password").val("")
                $("#chapa_input").val("")
                $("[permission]").each((i, el) => {
                    el.checked = false
                })
            },
            error: (e) => {
                console.log(e)
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

    $("#copy_rfid").on("click", () => {
        $("#rfid").val(MainProperties["rfid"])
    })

    $("#delete_user").on("click", () => {
        if ($("#users").val() == 0) return
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
                    url: "/users/delete/" + $("#users").val(),
                    type: "DELETE",
                    success: () => {
                        Swal.fire("Sucesso!", "", "success")
                        loadUsers()
                        $("#nome").val("")
                        $("#rfid").val("")
                        $("#password").val("")
                        $("#chapa_input").val("")
                        $("[permission]").each((i, el) => {
                            el.checked = false
                        })
                    }
                })
            }
        })
    })

    customInterval = setInterval(() => {
        if ($("#engenharia")[0].checked) {
            $("#password_container").removeAttr("hidden")
        } else {
            $("#password_container").attr("hidden", "hidden")
        }

        $(".card-rfid").text(`RFID: ${MainProperties["rfid"]}`)
    }, 200)
})
