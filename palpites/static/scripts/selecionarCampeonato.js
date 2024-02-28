function redirect(select) {
    var selectedOption = select.options[select.selectedIndex]
    var url = selectedOption.getAttribute('data-url')
    if (url) {
        window.location.href = url
    }
}
