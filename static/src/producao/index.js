$(document).ready(() => {
    let instructs = {
        consulta: {
            0: "Aguardando leitura da etiqueta",
            20: "Verificando etiqueta",
            25: "Consultando fluxo de rastreabilidade",
            26: "Aguardando autorização do líder",
            30: "Liberando ciclo",
            35: "Peça reprovada",
            40: "Aguardando finalização de ciclo da máquina",
            41: "Verificando e excluindo arquivos",
            42: "Salvando reprova",
            43: "Resetando ciclo",
            45: "Verificando e salvando arquivos",
            50: "Deletando informações antigas de retrabalho",
            51: "Salvando informações de rastreabilidade",
            52: "Removendo informações da linha",
            60: "Resetando ciclo"
        },
        etiqueta: {
            0: "Imprimindo etiqueta...",
            10: "Aguardando leitura da etiqueta",
            15: "Verificando etiqueta lida",
            20: "Peça reprovada",
            25: "Liberando ciclo",
            30: "Aguardando julgamento da máquina",
            33: "Excluindo arquivos de rastreabilidade - peça reprovada",
            34: "Salvando informações de reprova",
            35: "Salvando arquivos de rastreabilidade",
            40: "Salvando informações de rastreabilidade",
            50: "Resetando ciclo",
        },
        subEtiqueta: {
            0: "Aguardando leitura da etiqueta",
            5: "Verificando retrabalho",
            10: "Consultando fluxo de rastreabilidade",
            15: "Verificando rastreabilidade da peça",
            16: "Aguardando autorização do líder",
            20: "Imprimindo nova etiqueta",
            30: "Aguardando leitura da etiqueta gerada",
            35: "Verificando etiqueta lida",
            40: "Liberando ciclo",
            41: "Peça reprovada",
            50: "Aguardando julgamento da máquina",
            51: "Salvando informações de reprova - Peça reprovada",
            55: "Verificando e guardando arquivos",
            60: "Salvando informações de rastreabilidade",
            70: "Resetando ciclo"
        },
        consulta_cod: {
            0: "Enviando julgamento",
            10: "Aguardando a leitura do Código",
            20: "Verificando código"
        }
    }
    let configs = MainProperties["Cycle"]["configs"]
    let mode = configs["etiqueta"] == "true" ? "etiqueta" : configs["consulta"] == "true" ? "consulta" : configs["subEtiqueta"] == "true" ? "subEtiqueta" : "consulta_cod"

    $(".reset_ciclo").on("click", () => {
        if (mode == "etiqueta" || mode == "consulta") {
            if (MainProperties["Cycle"]["passo"] <= 10) {
                $.ajax({
                    url: "/resetCycle"
                })
            }
        } else {
            if (MainProperties["Cycle"]["passo"] <= 20) {
                $.ajax({
                    url: "/resetCycle"
                })
            }
        }

    })

    $(".instrucao").on("click", () => {
        $("#inst").css("display", "grid");
        $("#inst").modal("show");
    });

    $("#close_inst").on("click", () => {
        $("#inst").modal("hide");
    });

    $(".zera_estatisticas").on("click", () => {
        $.ajax({
            url: "/zeraContador"
        })
    })

    $("#ponta_estoque").on("click", () => {
        $.ajax({
            url: "/setPontaEstoque"
        })
    })


    let modal_retrabalho = false

    customInterval = setInterval(() => {
        if (MainProperties.ponta_estoque) {
            $("#ponta_estoque").addClass("btn-primary")
            $("#ponta_estoque").removeClass("btn-outline-secondary")
        } else {
            $("#ponta_estoque").removeClass("btn-primary")
            $("#ponta_estoque").addClass("btn-outline-secondary")
        }

        console.log(mode)

        if (mode == "etiqueta" || mode == "consulta") {
            if (MainProperties["Cycle"]["passo"] > 10) {
                $(".reset_ciclo").attr("disabled", "disabled")
            } else {
                $(".reset_ciclo").removeAttr("disabled")
            }
        } else {
            if (MainProperties["Cycle"]["passo"] > 20) {
                $(".reset_ciclo").attr("disabled", "disabled")
            } else {
                $(".reset_ciclo").removeAttr("disabled")
            }
        }

        $(".aprovado").text(MainProperties.Cycle.aprovados)
        $(".reprovado").text(MainProperties.Cycle.reprovados)
        $(".passo").html(instructs[mode][MainProperties["Cycle"]["passo"]])

        let code = MainProperties["Scanner"]["last_readed"]

        $("#codAtual").text(code.slice(0, 11))
        $("#cliente").text(code.slice(11, 16))
        $("#sequencial").text(code.slice(16, 21))
        $("#juliano").text(code.slice(21, 24))
        $("#ano").text(code.slice(24, 26))
        if (MainProperties["Cycle"]["msg"]) {
            $(".msg").html(MainProperties["Cycle"]["msg"])
            $(".msg").removeClass("d-none")
        } else {
            $(".msg").addClass("d-none")
        }

        if (MainProperties["Cycle"]["status_rastreabilidade"] == null) {
            $(".status-rastreabilidade").addClass("btn-outline-secondary")
            $(".status-rastreabilidade").removeClass("btn-danger")
            $(".status-rastreabilidade").removeClass("btn-success")
        } else if (MainProperties["Cycle"]["status_rastreabilidade"]) {
            $(".status-rastreabilidade").removeClass("btn-outline-secondary")
            $(".status-rastreabilidade").removeClass("btn-danger")
            $(".status-rastreabilidade").addClass("btn-success")
        } else {
            $(".status-rastreabilidade").removeClass("btn-outline-secondary")
            $(".status-rastreabilidade").addClass("btn-danger")
            $(".status-rastreabilidade").removeClass("btn-success")
        }

        if (MainProperties["Cycle"]["status_final"] == null) {
            $(".status-final").addClass("btn-outline-secondary")
            $(".status-final").removeClass("btn-danger")
            $(".status-final").removeClass("btn-success")
        } else if (MainProperties["Cycle"]["status_final"]) {
            $(".status-final").removeClass("btn-outline-secondary")
            $(".status-final").removeClass("btn-danger")
            $(".status-final").addClass("btn-success")
        } else {
            $(".status-final").removeClass("btn-outline-secondary")
            $(".status-final").addClass("btn-danger")
            $(".status-final").removeClass("btn-success")
        }

        if (MainProperties["Cycle"]["retrabalho"]) {
            if (modal_retrabalho)
                return
            modal_retrabalho = true
            Swal.fire({
                title: 'Peça de retrabalho',
                text: "Deseja continuar com retrabalho?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sim'
            }).then((result) => {
                if (result.isConfirmed) {
                    $.ajax({
                        url: "/retrabalho/1",
                        success: () => {
                            Swal.fire({
                                title: 'Aguardando crachá do líder!',
                                didOpen: () => {
                                    Swal.showLoading()
                                },
                            })

                            let cracha_interval = setInterval(() => {
                                if (MainProperties["Cycle"]["passo"] != 5) {
                                    Swal.close()
                                    clearInterval(cracha_interval)
                                }
                            })
                        }
                    })
                } else {
                    $.ajax({
                        url: "/retrabalho/0"
                    })
                }
            })
        } else {
            modal_retrabalho = false
        }

    }, 100)
})