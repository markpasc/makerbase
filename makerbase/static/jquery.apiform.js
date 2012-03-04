(function ($) {

    $.fn.apiSubmit = function (options) {
        var $form = this;
        var inputData = {};
        $.each($form.find(':input'), function (i, input) {
            var $input = $(input);
            var name = $input.attr('name');
            if (name) {
                inputData[name] = $input.val();
            }
        });

        var settings = $.extend({
            url: $form.attr('action'),
            type: $form.attr('method'),
            dataType: 'json',  // received
            contentType: 'application/json',  // sent
            processData: false,
            data: $.toJSON(inputData)
        }, options);

        $.ajax(settings);
    }

    $.fn.apiForm = function (options) {
        return this.on('submit', function () {
            try {
                $(this).apiSubmit(options);
            }
            catch (e) {
                console.log(e);
            };
            return false;
        });
    };

})(jQuery);
