const changePageEvent = new CustomEvent("changePage");
let MainProperties = {}
let customInterval
function changePage(url) {
  if (customInterval) {
    clearInterval(customInterval)
  }
  document.dispatchEvent(changePageEvent);
  $("#mainContent").load(url, function () { });
  $("#sidebar").removeClass("active");
  $(".overlay").removeClass("active");
}


function useAjax(path, form_data, method) {
  return new Promise(async (resolve, reject) => {
      let response
      if (method.toLowerCase() == "post") {
          response = await $.ajax({
              url: path,
              method: "POST",
              cache: false,
              contentType: false,
              processData: false,
              data: form_data
          })
      } else if (method.toLowerCase() == "get") {
          response = await $.ajax({
              url: path,
              method: "GET",
          })
      }

      resolve(response)
  })
}


function changeFootText(text) {
  $("#footerText").text(text);
}

function clear() {
  $(".active").each((i, el) => {
    $(el).removeClass("active");
  });

  $("#mainHeader").slideUp();
  $("#mainContent").css("min-height", "95vh");
  $("a[aria-expanded=true]").attr("aria-expanded", "false");
  $(".collapse").removeClass("show");
}

function setupHome() {
  $(".active").each((i, el) => {
    $(el).removeClass("active");
  });
  $("#mainHeader").slideDown();
  $("#mainContent").css("min-height", "74vh");
  $("a[aria-expanded=true]").attr("aria-expanded", "false");
  $(".collapse").removeClass("show");
}

$(".side-menu-item").on("click", async function () {
  let page = this.getAttribute("page");
  let name = this.getAttribute("name");
  let selectedRecipe = true

  $("[aria-expanded='true']").each((i, el) => {
    if (el != this.children[0]) {
      $(el)
        .attr("aria-expanded", "false")
        .addClass("collapsed")
        .next()
        .removeClass("show");
    }
  });
  let hasChildren = this.getAttribute("hasChildren");
  if (hasChildren == "True") {
    if (this.children[0].getAttribute("aria-expand")) {
      $(this).addClass("active");
    } else {
      $(this).removeClass("active");
    }
    return;
  }

  if(page == "/producao") {
    selectedRecipe = await recipeSelector.fireSelectRecipe()
  }
  if (!selectedRecipe) return


  if (name == "Início") {
    setupHome();
  } else {
    clear();
  }
  $("#pageName").text(name);
  $(this).addClass("active");

  changePage(page);
});

$(".side-submenu-item").on("click", function () {
  let page = this.getAttribute("page");
  let name = this.getAttribute("name");
  clear();

  $("#pageName").text(name);
  $(this).addClass("active");

  changePage(page);
});

$(".reload").click(function () {
  document.location.href = "/"
})

toastr.options = {
  positionClass: "toast-bottom-right",
};

const main = () => {
  if (MainProperties.hasOwnProperty("Cycle")) {
    if (MainProperties["Cycle"]["configs"]["ultimo_posto"]) {
      $(".ultimo_posto").removeAttr("hidden")
    } else {
      $(".ultimo_posto").attr("hidden", "hidden")
    }
  }

  $.ajax({
    url: "/getProperties",
    cache: false,
    success: (res) => {
      MainProperties = res.properties
      if (document.URL.split("//")[1].split(":")[0] == "127.0.0.1") {
        if (MainProperties["rfid"] != "") {
          $("#chapa").text(MainProperties["user"]["chapa"])
          $("#workerName").text(MainProperties["user"]["nome"])
          if (MainProperties["user"]["permissions"]["Administrador"]) {
            $(`[access]`).removeAttr("hidden")
          } else {
            Object.entries(MainProperties["user"]["permissions"]).forEach(([key, value]) => {
              if (value) {
                $(`[access=${key}]`).removeAttr("hidden")
              } else {
                $(`[access=${key}]`).attr("hidden", "hidden")
              }
            })
          }
        } else {
          $("[access]").attr("hidden", "hidden")
        }
      }
    }
  })
}

const authUser = () => {
  Swal.fire({
    title: "Entrar",
    html: `
  <div class="mb-3">
    <input type="text" class="form-control" id="chapa_login" placeholder="Chapa" />
  </div>
  <div class="mb-3">
    <input type="password" class="form-control" id="pass" placeholder="Senha" />
  </div>`,
    allowOutsideClick: false,
    allowEscapeKey: false,
    confirmButtonText: 'Logar',
    didOpen: () => {
      $.ajax({
        "url": "/users/getAll",
        type: "GET",
        success: (res) => {
          $("#users").empty()
          $("#users").append(
            $("<option>", { value: 0, text: "Selecione um usuário..." })
          )
          for (user of res.users) {
            if (user["permissions"]["Engenharia"])
              $("#users").append(

                $("<option>", { value: user["_id"], text: user["nome"] })
              )
          }
        }
      })
    },
    preConfirm: () => {
      if ($("#users").val() == 0) {
        Swal.fire("Selecione um usuário!", "", "info").then(() => {
          authUser()
        })
      }

      let chapa = $("#chapa_login").val()
      let pass = $("#pass").val()
      let formData = new FormData()

      formData.append("chapa", chapa)
      formData.append("pass", pass)

      $.ajax({
        url: "/authUser",
        type: "POST",
        dataType: "json",
        processData: false,
        cache: false,
        contentType: false,
        data: formData,
        success: (res) => {
          Swal.fire("Sucesso!", "", "success").then(() => {
            $("#chapa").text(res.user.chapa)
            $("#workerName").text(res.user.nome)
          })
        },
        error: (e) => {
          try {
            Swal.fire(e.responseJSON.msg, "", "error").then(() => {
              authUser()
            })
          } catch (e) {
            Swal.fire("Falha ao efetuar o login, tente novamente!", "", "error").then(() => {
              if (document.URL.split("//")[1].split(":")[0] != "127.0.0.1") {
                authUser()

              }
            })
          }
        }
      })
    }
  })
}

if (document.URL.split("//")[1].split(":")[0] != "127.0.0.1") {
  $("[local_only]").attr("hidden", "hidden")
  authUser()
}

function loadKeyboard() {
  KioskBoard.Run(".js-kioskboard-input", {
    keysArrayOfObjects: [
      {
        0: "Q",
        1: "W",
        2: "E",
        3: "R",
        4: "T",
        5: "Y",
        6: "U",
        7: "I",
        8: "O",
        9: "P",
      },
      {
        0: "A",
        1: "S",
        2: "D",
        3: "F",
        4: "G",
        5: "H",
        6: "J",
        7: "K",
        8: "L",
        9: "Ç",
      },
      {
        0: "Z",
        1: "X",
        2: "C",
        3: "V",
        4: "B",
        5: "N",
        6: "M",
        7: ",",
        8: ".",
        9: "/",
      },
    ],
    keysJsonUrl: null,
    specialCharactersObject: null,
    language: "pt-br",
    theme: "light",
    capsLockActive: false,
    allowRealKeyboard: true,
    cssAnimations: true,
    cssAnimationsDuration: 360,
    cssAnimationsStyle: "slide",
    keysAllowSpacebar: true,
    keysSpacebarText: "Space",
    keysFontFamily: "sans-serif",
    keysFontSize: "13px",
    keysFontWeight: "normal",
    keysIconSize: "13px",
    allowMobileKeyboard: true,
    autoScroll: true,
  });
}

setInterval(main, 100);

const recipeSelector = new RecipesSelector()
