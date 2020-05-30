// price formatter
function nFormatter(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
    }
    return num;
}

$(document).ready(function () {
    var price_range = parseInt($("#price_range").val());
    var rent_price_range = parseInt($("#rent_price_range").val());

    //location autocomplete
    $(function () {
        $("#location").on('keyup', function () {
            var value = $(this).val();
            $.ajax({
                url: '/autocomplete_location',
                data: {
                    'search': value
                },
                dataType: 'json',
                success: function (data) {
                    list = data.list;
                    $("#location").autocomplete({
                        source: list,
                        minLength: 2
                    });
                }
            });
        });
    });

    $(function () {
        $("#rent_location").on('keyup', function () {
            var value = $(this).val();
            $.ajax({
                url: '/autocomplete_location',
                data: {
                    'search': value
                },
                dataType: 'json',
                success: function (data) {
                    list = data.list;
                    $("#rent_location").autocomplete({
                        source: list,
                        minLength: 2
                    });
                }
            });
        });
    });

    //buy budget filter slider
    $(function () {
        $("#slider").slider({
            max: 10000000,
            min: 0,
            step: 50000,
            value: price_range,
            animate: "fast",
            range: "min",
            slide: function (event, ui) {
                if (ui.value >= 10000000) {
                    $("#price").html("$" + nFormatter(ui.value) + "+");

                } else if (ui.value < 10000000 && ui.value > 0) {
                    $("#price").html(" $0 - " + "$" + nFormatter(ui.value));
                } else {
                    $("#price").html(" Any");
                }
                $("#price_range").val(ui.value);
            },
        });
    });

    //rent budget filter slider
    $(function () {
        $("#rent_slider").slider({
            max: 1500,
            min: 0,
            step: 100,
            value: rent_price_range,
            animate: "fast",
            range: "min",
            slide: function (event, ui) {
                if (ui.value >= 1500) {
                    $("#rent_price").html("$" + ui.value + "+");

                } else if (ui.value < 1500 && ui.value > 0) {
                    $("#rent_price").html(" $0 - " + "$" + ui.value);
                } else {
                    $("#rent_price").html(" Any");
                }
                $("#rent_price_range").val(ui.value);
            },
        });
    });

    // click on buy tab
    $('#buy_tab').click(function () {
        $("#rent_div").addClass("d-none");
        $("#rent_tab").removeClass("active bg-light-grey")
        $("#rent_tab").addClass("bg-dark-grey")
        $("#buy_tab").removeClass("bg-dark-grey")
        $("#buy_tab").addClass("active bg-light-grey")
        $("#buy_div").removeClass("d-none");
    });

    // click on rent tab
    $('#rent_tab').click(function () {
        $("#buy_div").addClass("d-none");
        $("#buy_tab").removeClass("active bg-light-grey")
        $("#buy_tab").addClass("bg-dark-grey")
        $("#rent_tab").removeClass("bg-dark-grey")
        $("#rent_tab").addClass("active bg-light-grey")
        $("#rent_div").removeClass("d-none");
    });


    // index page submit forms
    function submit_buy_form() {
        document.querySelector('#filterForm_buy').submit();
    }

    function submit_rent_form() {
        document.querySelector('#filterForm_rent').submit();
    }

    //pagination
    $('.page-selection').each(function (index, element) {
        var search = $(this).data("search");
        var page = $(this).data("page");
        
        $(element).click(function () {
            if (search == 'rent') {
                $("#rent_page").val(page);
                submit_rent_form();
            } else {
                $("#buy_page").val(page);
                submit_buy_form();
            }
        });
    });

    //sort functions
    $('#most_recent').click(function () {
        if ($("#Selected_Search_form").val() == 'rent') {
            $("#sort_rent").val("MR");
            submit_rent_form();
        } else {
            $("#sort").val("MR");
            submit_buy_form();
        }
    });
    $('#location_A_Z').click(function () {
        if ($("#Selected_Search_form").val() == 'rent') {
            $("#sort_rent").val("AZ");
            submit_rent_form();
        } else {
            $("#sort").val("AZ");
            submit_buy_form();
        }
    });
    $('#location_Z_A').click(function () {
        if ($("#Selected_Search_form").val() == 'rent') {
            $("#sort_rent").val("ZA");
            submit_rent_form();
        } else {
            $("#sort").val("ZA");
            submit_buy_form();
        }
    });
    $('#most_expensive').click(function () {
        if ($("#Selected_Search_form").val() == 'rent') {
            $("#sort_rent").val("HL");
            submit_rent_form();
        } else {
            $("#sort").val("HL");
            submit_buy_form();
        }
    });
    $('#cheapest').click(function () {
        if ($("#Selected_Search_form").val() == 'rent') {
            $("#sort_rent").val("LH");
            submit_rent_form();
        } else {
            $("#sort").val("LH");
            submit_buy_form();
        }
    });

    // index page clear selection  for buy tab
    $('#clear_selections').click(function () {
        $('#property_type').val("ALL");
        $('#location').val("");
        $('#bedrooms').val("ANY");
        $('#bathrooms').val("ANY");
        $('#parking').val("ANY");
        $('#price_range').val(9000000);
        submit_buy_form();
    });

    // index page clear selection  for rent tab
    $('#rent_clear_selections').click(function () {
        $('#rent_property_type').val("ALL");
        $('#rent_location').val("");
        $('#rent_bedrooms').val("ANY");
        $('#rent_bathrooms').val("ANY");
        $('#rent_parking').val("ANY");
        $('#rent_price_range').val(1400);
        submit_rent_form();
    });

    //send message to seller
    $('#send_message').click(function () {
        $('#overlay_message').show();
    });
    $('#cancel_message').click(function () {
        $("#return_message").hide();
        $("#message").val("");
        $('#overlay_message').hide();
    });

    $("#form_send_message").submit(function () {
        $(".spinner").removeClass("d-none");
        $.ajax({
            type: "POST",
            url: '/send_message',
            data: {
                'ad_id': $("#ad_id").val(),
                'ad_type': $("#ad_type").val(),
                'first_name': $("#first_name").val(),
                'last_name': $("#last_name").val(),
                'email': $("#email").val(),
                'mobile': $("#mobile").val(),
                'message': $("#message").val(),
            },
            headers: {
                'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
            },
            dataType: 'json',
            success: function (data) {
                if (data.result == 'SUCCESS') {
                    $(".spinner").addClass("d-none");
                    $("#return_message").removeClass("d-none");
                    $("#return_message").html("Message sent!");
                    $("#message").val("");

                } else {
                    $(".spinner").addClass("d-none");
                    $("#return_message").removeClass("d-none");
                    $("#return_message").html("Error sending message!");
                    $("#message").val("");
                }

            }
        });
        event.preventDefault();
    });

    $(".custom-file-input").on("change", function () {
        var fileName = $(this).val().split("\\").pop();
        $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
    });

    $('#auction_clear').click(function () {
        $('#action_date').val("");
        return false;
    });

    // payment package selection - standard, for sale of properties
    $('#btn_std').click(function () {
        $("#prm_select").addClass("d-none");
        $("#card-prm").addClass("pkg-not-selected");
        $("#card-prm").removeClass("pkg-selected");

        $("#std_select").removeClass("d-none");
        $("#card-std").removeClass("pkg-not-selected");
        $("#card-std").addClass("pkg-selected");
        $("#payment_pkg").val("STD");
        return false;
    });

    // payment package selection - premium, for sale of properties
    $('#btn_prm').click(function () {
        $("#prm_select").removeClass("d-none");
        $("#card-prm").removeClass("pkg-not-selected");
        $("#card-prm").addClass("pkg-selected");

        $("#std_select").addClass("d-none");
        $("#card-std").addClass("pkg-not-selected");
        $("#card-std").removeClass("pkg-selected");

        $("#payment_pkg").val("PRM");
        return false;
    });

    // payment package selection - standard, for rental properties
    $('#rent_btn_std').click(function () {
        $("#rent_prm_select").addClass("d-none");
        $("#rent-card-prm").addClass("pkg-not-selected");
        $("#rent-card-prm").removeClass("pkg-selected");

        $("#rent_std_select").removeClass("d-none");
        $("#rent-card-std").removeClass("pkg-not-selected");
        $("#rent-card-std").addClass("pkg-selected");
        $("#rent_payment_pkg").val("STD");
        return false;
    });

     // payment package selection - premium, for rental properties
    $('#rent_btn_prm').click(function () {
        $("#rent_prm_select").removeClass("d-none");
        $("#rent-card-prm").removeClass("pkg-not-selected");
        $("#rent-card-prm").addClass("pkg-selected");

        $("#rent_std_select").addClass("d-none");
        $("#rent-card-std").addClass("pkg-not-selected");
        $("#rent-card-std").removeClass("pkg-selected");
        $("#rent_payment_pkg").val("PRM");
        return false;
    });


    // inspection date & time clear anchor tag for sale of property
    $('a[id^="insp_clear_"]').each(function (index, element) {

        var counter = $(this).data("insp-counter");
        $(element).click(function () {
            $('#ins_date_' + counter.toString()).val("");
            $('#ins_from_time_' + counter.toString()).val("");
            $('#ins_to_time_' + counter.toString()).val("");
            return false;
        });
    });

    // inspection date & time clear anchor tag for rental property
    $('a[id^="rent_insp_clear_"]').each(function (index, element) {

        var counter = $(this).data("insp-counter");
        $(element).click(function () {
            $('#rent_ins_date_' + counter.toString()).val("");
            $('#rent_ins_from_time_' + counter.toString()).val("");
            $('#rent_ins_to_time_' + counter.toString()).val("");
            return false;
        });
    });

    // floor plan viewer
    $('#view_floorplan').click(function () {
        $('#overlay_floorplan').show();
    });
    $('#cancel_floorplan').click(function () {
        $('#overlay_floorplan').hide();
    });

});
