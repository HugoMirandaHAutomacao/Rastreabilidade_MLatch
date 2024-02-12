$(document).ready(function () {
    if (document.URL.split("//")[1].split(":")[0] == "127.0.0.1") {
        loadKeyboard()
    }
    $("#producao-img").on("input", function () {
        var form_data = new FormData();
        var ins = this.files.length;


        for (var x = 0; x < ins; x++) {
            form_data.append("files[]", this.files[x]);
        }

        $.ajax({
            url: '/changeImage',
            cache: false,
            contentType: false,
            processData: false,
            data: form_data,
            type: 'post'
        }).then(() => {
            Swal.fire("Imagem atualizada com sucesso!", "", "success")
        })
    })
    $("#producao-pdf").on("input", function () {
        var form_data = new FormData();
        var ins = this.files.length;

        for (var x = 0; x < ins; x++) {
            form_data.append("files[]", this.files[x]);
        }

        $.ajax({
            url: '/changePDF',
            cache: false,
            contentType: false,
            processData: false,
            data: form_data,
            type: 'post'
        }).then(() => {
            Swal.fire("PDF atualizado com sucesso!", "", "success")
        })
    })

    $("#delete-db").on("click", () => {
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
                    url: "/deleteDb",
                    type: "DELETE",
                    success: () => {
                        Swal.fire("Sucesso!", "", "success")
                    }
                })
            }
        })
    })


    $.ajax({
        "url": "/getConfig",
        type: "GET",
        success: (res) => {
            console.log(res.configs)
            $("#ip").val(MainProperties.Cycle.configs.ip)
            $("#netmask").val(MainProperties.Cycle.configs.netmask)
            $("#gateway").val(MainProperties.Cycle.configs.gateway)
            $("#etiqueta")[0].checked = MainProperties.Cycle.configs.etiqueta == "true"
            $("#subEtiqueta")[0].checked = MainProperties.Cycle.configs.subEtiqueta == "true"
            $("#consulta")[0].checked = MainProperties.Cycle.configs.consulta == "true"
            $("#ftp")[0].checked = MainProperties.Cycle.configs.ftp == "true"
            $("#leitura_plc")[0].checked = MainProperties.Cycle.configs.leitura_plc == "true"
            $("#ip_consulta").val(MainProperties.Cycle.configs.ip_consulta)
            $("#ip_impressora").val(MainProperties.Cycle.configs.ip_impressora)
            $("#ultimo_posto").val(MainProperties.Cycle.configs.ultimo_posto)
            $("#cod_unico").val(MainProperties.Cycle.configs.cod_unico)
            $("#tipo_etiqueta").val(MainProperties.Cycle.configs.tipo_etiqueta)
            $("#nome_totem").val(MainProperties.Cycle.configs.nome_totem)
            $("#qntd_ftp").val(MainProperties.Cycle.configs.qntd_ftp)
            $("#ip_ultimo_posto").val(MainProperties.Cycle.configs.ip_ultimo_posto)
            $("#scanner_com_port").val(MainProperties.Cycle.configs.scanner_com_port)
            $("#rfid_com_port").val(MainProperties.Cycle.configs.rfid_com_port)
            $("#ultimo_posto")[0].checked = MainProperties.Cycle.configs.ultimo_posto == "true"
            $("#consultaCodigo")[0].checked = MainProperties.Cycle.configs.consulta_cod == "true"
        }
    })

    $("#form-config").on("submit", (e) => {
        e.preventDefault()

        let ip = $("#ip").val()
        let netmask = $("#netmask").val()
        let gateway = $("#gateway").val()
        let etiqueta = $("#etiqueta")[0].checked
        let subEtiqueta = $("#subEtiqueta")[0].checked
        let consulta = $("#consulta")[0].checked
        let ftp = $("#ftp")[0].checked
        let leitura_plc = $("#leitura_plc")[0].checked
        let ip_consulta = $("#ip_consulta").val()
        let cod_unico = $("#cod_unico").val()
        let ip_impressora = $("#ip_impressora").val()
        let tipo_etiqueta = $("#tipo_etiqueta").val()
        let qntd_ftp = $("#qntd_ftp").val()
        let nome_totem = $("#nome_totem").val()
        let ip_ultimo_posto = $("#ip_ultimo_posto").val()
        let scanner_com_port = $("#scanner_com_port").val()
        let rfid_com_port = $("#rfid_com_port").val()
        let ultimo_posto = $("#ultimo_posto")[0].checked
        let consultaCod = $("#consultaCodigo")[0].checked
        


        let formData = new FormData()

        formData.append("ip", ip)
        formData.append("netmask", netmask)
        formData.append("gateway", gateway)
        formData.append("etiqueta", etiqueta)
        formData.append("subEtiqueta", subEtiqueta)
        formData.append("consulta", consulta)
        formData.append("ftp", ftp)
        formData.append("ip_consulta", ip_consulta)
        formData.append("cod_unico", cod_unico)
        formData.append("ip_impressora", ip_impressora)
        formData.append("tipo_etiqueta", tipo_etiqueta)
        formData.append("nome_totem", nome_totem)
        formData.append("qntd_ftp", qntd_ftp)
        formData.append("leitura_plc", leitura_plc)
        formData.append("ip_ultimo_posto", ip_ultimo_posto)
        formData.append("scanner_com_port", scanner_com_port)
        formData.append("rfid_com_port", rfid_com_port)
        formData.append("ultimo_posto", ultimo_posto)
        formData.append("consultaCod", consultaCod)
        Swal.fire({
            title: 'Salvando configurações!',
            didOpen: () => {
                Swal.showLoading()
            },
        })
        $.ajax({
            url: "/updateConfig",
            type: "PUT",
            dataType: "json",
            processData: false,
            cache: false,
            contentType: false,
            data: formData,
            success: () => {
                Swal.fire("Sucesso", "", "success")
            }, error: (e) => {
                Swal.fire(e.responseJSON.msg, "", "error")
            }
        })
    })

    customInterval = setInterval(() => {
        if ($("#etiqueta")[0].checked) {
            $("#ip_consulta_container").attr("hidden", "hidden")
        } else {
            $("#ip_consulta_container").removeAttr("hidden")
        }
        if ($("#consulta")[0].checked) {
            $("#ip_impressora_container").attr("hidden", "hidden")
        } else {
            $("#ip_impressora_container").removeAttr("hidden")
        }
        if ($("#ftp")[0].checked) {
            $("#qntd_ftp_container").removeAttr("hidden")
        } else {
            $("#qntd_ftp_container").attr("hidden", "hidden")
        }

        $("#rfid_read").val(MainProperties["rfid"])
        $("#scanner_read").val(MainProperties["Scanner"]["readed"])
    }, 300)
})