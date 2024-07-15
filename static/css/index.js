const confirmaBorrado = document.querySelectorAll("#botonBorrar")

if (confirmaBorrado.length){
    for (const boton of confirmaBorrado){
        boton.addEventListener("click", event =>{
            respuesta = confirm("Desea borrar el registro. Confirma?")
            if (!respuesta) {
                event.preventDefault()
            }
        })
    }
}
