$("#filter").change(function() {
    var filter = $(this).find(":selected").val();
    $("#image").attr("class", filter);
});
