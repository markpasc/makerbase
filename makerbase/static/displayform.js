(function ($) {

    $.fn.displayForm = function (options) {
        // Do each form separately so our functions wrap each particular form.
        return this.each(function () {
            var $form = $(this);
            var settings = $.extend({
                submit: function () {
                    $form.find('.control-group').removeClass('error');
                    $form.find('.inline-error').hide();
                },
                success: function (data) {
                    window.location.reload();
                },
                error: function (jqxhr, textStatus, errorThrown) {
                    var data = $.parseJSON(jqxhr.responseText);
                    $.each(data.errors, function (key, val) {
                        var $input = $form.find('input[name="' + key + '"]');
                        var $group = $input.parents('.control-group');
                        $group.addClass('error');

                        var $message = $group.find('.help-inline');
                        if (!$message.size()) {
                            $message = $('<span/>').addClass('help-inline').addClass('inline-error');
                            $message.appendTo($group);
                        }
                        $message.text(val.join('. '));
                        $message.show();
                    });
                }
            }, options);

            return $form.apiForm(settings);
        });
    };

})(jQuery);
