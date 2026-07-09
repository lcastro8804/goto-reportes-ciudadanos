document.addEventListener("DOMContentLoaded", () => {
    const radios = document.querySelectorAll('input[name="criterio"]');
    const campo = document.getElementById("campo-consulta");

    if (!radios.length || !campo) {
        return;
    }

    const actualizarPlaceholder = () => {
        const activo = document.querySelector('input[name="criterio"]:checked');
        campo.placeholder = activo && activo.value === "folio" ? "20260001" : "5527295528";
    };

    radios.forEach((radio) => {
        radio.addEventListener("change", actualizarPlaceholder);
    });

    actualizarPlaceholder();
});
