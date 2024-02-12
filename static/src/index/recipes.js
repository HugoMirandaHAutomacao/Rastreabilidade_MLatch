let recipesSelector


class Receita {
    constructor(id, cod, name) {
        this.id = id
        this.cod = cod
        this.name = name
    }

}


class RecipesSelector {
    constructor() {
        self.receitas = {}
        this.loadRecipes()
    }

    getRecipes = () => {
        return self.receitas
    }

    loadRecipes = async () => {
        self.receitas = []
        const recipesList = await useAjax("/receitas/getAll", "", "GET")
        for (let recipe of recipesList.recipes) {
            const newRecipe = new Receita(recipe._id, recipe.codigo, recipe.nome)
            self.receitas[recipe._id] = newRecipe
        }
    }

    loadDropdownRecipes = async () => {
        const body = $("#swal2-html-container #selectRecipe")
        body.empty()
        body.append(`<option value="" selected>Selecione uma receita</option>`)
      
        for (let receita of Object.values(this.getRecipes())) {
            body.append(`<option value="${receita.id}">${receita.name}</option>`)
        }
    }

    fireSelectRecipe = async () => {
        return new Promise((resolve, reject) => {
          Swal.fire({
            title: "Selecione uma receita",
            html: `<div class="w-100 d-flex align-items-center justify-content-center"> 
                        <select id="selectRecipe" class="select w-75" aria-label="Default select example"></select>
                   </div>`,
            showConfirmButton: true,
            showDenyButton: true,
            confirmButtonText: "Confirmar",
            denyButtonText: "Cancelar",
            didOpen: async () => {
                await this.loadDropdownRecipes()
                $(".swal2-confirm").prop("disabled", true)
                $("#swal2-html-container #selectRecipe").on("change", function () { $(".swal2-confirm").prop("disabled", !$(this).val()) })
            },
          }).then(async (result) => {

            if(result.isConfirmed) {
                const selectedRecipe = $("#swal2-html-container #selectRecipe").val()
                await this.assignRecipe(selectedRecipe)
                resolve(true)
            }
            resolve(false)
          })
      
      
        })
      }

    assignRecipe = async (recipeID) => {
       const formData = new FormData()
        formData.append("recipeId", recipeID)

       const response = await useAjax("/setRecipe", formData, "POST")
       if(response.status == 0) toastr.success("Receita alterada com sucesso")
    }
}