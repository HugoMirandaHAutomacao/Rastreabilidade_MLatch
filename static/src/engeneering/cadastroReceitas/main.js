$(document).ready(function () {
  loadKeyboard()

  const updateRecipeList = async () => {
    const body = $("#recipesSelect")
    body.empty()
    body.append(`<option value="" selected>Selecione uma receita</option>`)

    for (let receita of Object.values(recipeSelector.getRecipes())) {
      body.append(`<option value="${receita.id}">${receita.name}</option>`)
    }
  }

  const formDataConstructor = async () => {
    const formData = new FormData()
    const components = Array.from($("[formComponent]"))
    for (let formComp of components) {
      const elemVal = $(formComp).val()
      const elemKey = $(formComp).attr("id")
      if (!elemVal) return null
      formData.append(elemKey, elemVal)
    }
    return formData
  }

  const resetInputs = () => {
    $("[formComponent]").val("")
  }

  const fireConfirmation = (text, icon) => {
    return new Promise((resolve, reject) => {
      Swal.fire({
        title: "Confirmação",
        text: text,
        icon: icon,
        showDenyButton: true,
        showConfirmButton: true,
        denyButtonText: "Não",
        confirmButtonText: "Sim"
      }).then((result) => {
        if (result.isConfirmed) resolve(true)
        resolve(false)
      })
    })
  }


  $("#recipesSelect").on("change", function () {
    const recipeVal = $(this).val()

    resetInputs()
    if (!recipeVal) return

    $("[formComponent]").each((indx, el) => {
      const dictKey = $(el).attr("id")
      $(el).val(recipeSelector.getRecipes()[recipeVal][dictKey])
    })

  })

  $("#updateRecipe").on("click", async function () {
    const recipeID = $("#recipesSelect").val()
    if (!recipeID) return Swal.fire("Erro", "Selecione uma receita", "info")

    const formDataOrNull = await formDataConstructor()
    if (!formDataOrNull) return Swal.fire("Campos não preenchidos", "Preencha todos os campos", "info")

    const updateConfirmed = await fireConfirmation("Tem certeza de que deseja alterar esta receita?", "question")
    if (!updateConfirmed) return

    formDataOrNull.append("id", recipeID)
    const response = await useAjax("/receitas/update", formDataOrNull, "POST")
    if (response.status == 0) {
      Swal.fire("Sucesso", "Receita alterada com sucesso", "success")
      await recipeSelector.loadRecipes()
      await updateRecipeList()
    } else {
      Swal.fire("Erro", response.message, "error")
    }

  })

  $("#deleteRecipe").on("click", async function () {
    const recipeID = $("#recipesSelect").val()
    if (!recipeID) return Swal.fire("Erro", "Selecione uma receita", "info")

    const deleteConfirmed = await fireConfirmation("Tem certeza de que deseja alterar esta receita?", "warning")
    if (!deleteConfirmed) return

    const formData = new FormData()
    formData.append("id", recipeID)
    const response = await useAjax("/receitas/delete", formData, "POST")
    if (response.status == 0) {
      Swal.fire("Sucesso", "Receita excluida com sucesso", "success")
      await recipeSelector.loadRecipes()
      await updateRecipeList()
    }

  })

  $("#registerRecipe").on("click", async function () {
    const formDataOrNull = await formDataConstructor()
    if (!formDataOrNull) return Swal.fire("Campos não preenchidos", "Preencha todos os campos", "info")

    const response = await useAjax("/receitas/register", formDataOrNull, "POST")
    if (response.status == 0) {
      Swal.fire("Sucesso", "Receita cadastrada com sucesso", "success")
      await recipeSelector.loadRecipes()
      await updateRecipeList()
    } else {
      Swal.fire("Erro", response.message, "error")
    }
  })

  updateRecipeList()
})