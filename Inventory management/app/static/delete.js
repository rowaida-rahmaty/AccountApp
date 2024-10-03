$(document).ready(function () {
    $(".close").click(function () {
        var messageId = $(this).data("message-id");  // Retrieve the message ID

        $.ajax({
            url: "{{ url_for('views.delete_flash_message') }}",
            type: "POST",
            data: JSON.stringify({ "message_id": messageId }),
            contentType: "application/json",
            success: function (response) {
                if (response.success) {
                    $("div[data-message-id='" + messageId + "']").remove();  // Remove the message from the DOM
                } else {
                    console.error("Failed to delete the message.");
                }
            },
            error: function (xhr, status, error) {
                console.error("AJAX request failed: " + error);
            }
        });
    });
});
