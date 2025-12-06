/* Fix Forms */
/*
$('select:not(#id_item)').addClass('select2');
$('.select2:not(#id_item)').select2();
$('.select2-container').addClass('form-control');
*/
$(':input:not(:checkbox, button, :radio)').addClass('form-control');
$('textarea').addClass('form-control');
$('select').addClass('form-control');
$("form").submit(function (e) {
    $("#submit_btn").attr("disabled", true);
});

/* confirm delete */
$('.confirm-delete').on('click', function () {
    confirm('هل أنت متأكد من حذف هذا العنصر؟');
});


/* modals plugins by ON-Link */
$('#action_modal').on('show.bs.modal', function (e) {
    $('#action_body').load(e.relatedTarget.href);
});

$('#sub_modal').on('show.bs.modal', function (x) {
    $('#sub_body').load(x.relatedTarget.href);
});

$('#user_modal').on('show.bs.modal', function (y) {
    $('#user_body').load(y.relatedTarget.href);
});

$('body').on('hidden.bs.modal', function () {
    if ($('.modal.in').length > 0) {
        $('body').addClass('modal-open');
    }
});


