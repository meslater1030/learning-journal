$(document).ready(function(){
    $(".hide-on-start").hide();

    $('#edit-link').on('click', function(event){
        event.preventDefault();

        var id = $('#form-id').val();
        var title = $('#form-title').val();

        $.ajax({
            method: "GET",
            url: "/edit/" + id + "/" + title
        }).done(function(response){
            $("#form-title").val();
            $('#form-text').val();
            $('.entry').hide();
            $('#edit-form-container').show();
        }).fail(function(){
            alert("error");
        });
    });

    $('#update-link').on('click', function(event){
        event.preventDefault();

        var id = $('#form-id').val();
        var title = $('#form-title').val();
        var text = $('#form-text').val();

        $.ajax({
            method: 'POST',
            url: '/edit/' + id + '/' + title,
            data: {id: id, text: text, title: title},
        }).done(function(response){
            $('#entry-title').html(response.entry.title);
            $('#entry-text').html(response.entry.text);
            $('.entry').show();
            $('#edit-form-container').hide();
        }).fail(function(){
            alert("error");
        });
    });
})