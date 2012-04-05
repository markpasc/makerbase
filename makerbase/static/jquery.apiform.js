(function ($) {

    $.fn.apiData = function (options) {
        var $form = this;
        var inputData = {};
        $.each($form.find(':input'), function (i, input) {
            var $input = $(input);
            var name = $input.attr('name');
            if (name) {
                inputData[name] = $input.val();
            }
        });
        return inputData;
    };

    $.fn.apiSubmit = function (options) {
        var $form = this;
        var settings = $.extend({
            url: $form.attr('action'),
            type: $form.attr('method'),
            dataType: 'json',  // received
            contentType: 'application/json',  // sent
            processData: false
        }, options);
        // Don't bother computing the data if options had one.
        if (!settings.hasOwnProperty('data')) {
            settings['data'] = $.toJSON($form.apiData());
        }

        if (settings.hasOwnProperty('submit')) {
            settings['submit']($form);
        }

        return $.ajax(settings);
    };

    $.fn.apiForm = function (options) {
        return this.on('submit', function () {
            $(this).apiSubmit(options);
            return false;
        });
    };

})(jQuery);
