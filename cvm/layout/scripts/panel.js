function updateElementIndex(el, prefix, ndx) {
    // var id_regex = new RegExp('(' + prefix + '-\\d+-)');
    var id_regex = prefix + '-__prefix__-';
    var replacement = prefix + '-' + ndx + '-';
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}
function deleteForm(btn, prefix) {
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (formCount > 1) {
        // Delete the item/form
        $(btn).parents('.formset_row').remove();
        var forms = $('.formset_row'); // Get all the forms
        // Update the total number of forms (1 less than before)
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        var i = 0;
        // Go through the forms and set their indices, names and IDs
        for (formCount = forms.length; i < formCount; i++) {
            $(forms.get(i)).children().children().each(function() {
                if ( $(this).attr('type') == 'text' )
                    updateElementIndex(this, prefix, i);
            });
        }
    } // End if
    else {
        alert("You have to enter at least one todo item!");
    }
    return false;
}
function addForm(btn, prefix) {
    var formCounter = $('#id_' + prefix + '-TOTAL_FORMS');
    var formCount = parseInt(formCounter.val());
    // Clone a form (without event handlers) from the first form
    var prefix_row = $('#formset_row_' + prefix + '-__prefix__');
    var row = prefix_row.clone(false).get(0);
    // Insert it after the last form
    $(row).insertBefore($(btn).parent().parent()).slideDown(300);
    // Relabel or rename all the relevant bits
    $(row).find('input, textarea').each(function() {
        updateElementIndex(this, prefix, formCount);
        $(this).val("");
    });
    // Add an event handler for the delete item/form link
    $(row).find(".delete").click(function() {
        return deleteForm(this, prefix);
    });
    // Update the total form count
    formCounter.val(formCount + 1);
    $(row).find('.date-picker a.dp-choose-date').remove();
    $(row).find('.date-picker input').datePicker({startDate: '01/01/1900'})
    return false;
}
