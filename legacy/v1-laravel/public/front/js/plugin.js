$(document).ready(function(){

    $(".dropdown-menu.cart-dropdown").on("click", function (e) {
        e.preventDefault();
    });

    /**  Start Progress Script
     **=========================================== **/
    $(".cafe-rate-progress").each(function () {
        var circle = new ProgressBar.Circle("#" + $(this).attr("id"), {
            strokeWidth: 5,
            easing: 'easeInOut',
            duration: 0,
            color: "#6F6DFF",
            trailColor: '#EDF2F5',
            trailWidth: 5,
            text: {
                value: '0',
                style: {
                    color: '#707070',
                    position: 'absolute',
                    left: '50%',
                    top: '50%',
                    padding: 0,
                    margin: 0,
                    fontWeight: "bold",
                    fontSize: "11px",
                    transform: {
                        prefix: true,
                        value: 'translate(-50%, -50%)'
                    }
                }
            },
            svgStyle: {
                display: 'inline-block',
                width: '50'
            },
            step: (state, bar) => {
                bar.setText(Math.round(bar.value() * 100));
            }
        });
        circle.animate($(this).data('value'));
    });

   // best selling slider
    var sellingSwipper = new Swiper('.best-order-slider', {
        observer: true,
        loop: true,
        effect: 'flip',
        slidesPerView: 1,
        pagination: {
            el: '.best-selling-pagination',
            clickable: true,
        },

    });

    // orders slider
    var orderSwiper = new Swiper('.orders-swiper', {
        observer: true,
        slidesPerView: 1,
        slidesPerColumn: 3,
        spaceBetween: 15,
        pagination: {
            el: '.orders-pagination',
            clickable: true,
        },
        breakpoints: {
            991 : {
                slidesPerColumn: 1,
            },
            767 : {

            }
        }
    });

    // top cafe slider
    var cafesSwiper = new Swiper('.cafes-swiper-slider', {
        //speed: 400,
        observer: true,
        loop: true,
        slidesPerView: 2,
        spaceBetween: 30,
        paginationClickable: true,
        pagination: {
            el: '.top-cafe-pagination',
            clickable: true,
        },
        // Navigation arrows
        navigation: {
            nextEl: '.top-cafe-slider-next',
            prevEl: '.top-cafe-slider-prev',
            clickable: true,
        },
        breakpointsInverse: true,
        breakpoints: {
            575 : {
                slidesPerView: 3,
            },

            767 : {
                slidesPerView: 4,
            },
            991: {
                slidesPerView: 6,
            }
        }
    });

    /*
 * Replace all SVG images with inline SVG
 */
    jQuery('img.svg').each(function(){
        var $img = jQuery(this);
        var imgID = $img.attr('id');
        var imgClass = $img.attr('class');
        var imgURL = $img.attr('src');

        jQuery.get(imgURL, function(data) {
            // Get the SVG tag, ignore the rest
            var $svg = jQuery(data).find('svg');

            // Add replaced image's ID to the new SVG
            if(typeof imgID !== 'undefined') {
                $svg = $svg.attr('id', imgID);
            }
            // Add replaced image's classes to the new SVG
            if(typeof imgClass !== 'undefined') {
                $svg = $svg.attr('class', imgClass+' replaced-svg');
            }

            // Remove any invalid XML tags as per http://validator.w3.org
            $svg = $svg.removeAttr('xmlns:a');

            // Check if the viewport is set, if the viewport is not set the SVG wont't scale.
            if(!$svg.attr('viewBox') && $svg.attr('height') && $svg.attr('width')) {
                $svg.attr('viewBox', '0 0 ' + $svg.attr('height') + ' ' + $svg.attr('width'))
            }

            // Replace image with new SVG
            $img.replaceWith($svg);

        }, 'xml');

    });


    $('.coffe-logo .slick-prev').html('<i class="fas fa-caret-left"></i>');
    $('.coffe-logo .slick-next').html('<i class="fas fa-caret-right"></i>');

    $('#cafe-tab a').on('click', function (e) {
        e.preventDefault()
        $(this).tab('show')
    });

    /*********[ Login & Register ]************/
    var loginPopupContent = $('#login-content'),
        registerPopupContent = $('#register-content');


    $('.login-register-pagination').on('click', function (e) {
        e.preventDefault();
       var showPage = $(this).data('target');
        $(showPage).addClass('active-register-login').siblings().removeClass('active-register-login')
    });

    // login & register modal
    $('.login-modal').click(function () {
        loginPopupContent.addClass('active-register-login').siblings().removeClass('active-register-login');
    });

    $('.register-modal').click(function () {
        registerPopupContent.addClass('active-register-login').siblings().removeClass('active-register-login');
    });

    var loginRegsiterInputs = $('.register-login .form-input .form-control');
    loginRegsiterInputs.on('focus', function () {
        $(this).parent().addClass('focusActive');
    });

    loginRegsiterInputs.on('focusout', function () {
        if ($(this).val() === "") {
            $(this).parent().removeClass('focusActive');
        }
    });

    loginRegsiterInputs.each(function () {
       if ($(this).val() !== "") {
           $(this).parent().addClass('focusActive');
       }
    });
    /*********[ Login & Register ]************/


    // address modal
    $('.address-modal-btn[data-toggle= "add-address"]').on("click", function (e) {
        e.preventDefault();
        var content_id= $(this).data('target');
        $("#"+ content_id).addClass('show-add-address-modal-content').siblings().removeClass('show-add-address-modal-content');
    });

    // payment modal
    $('.check-payment[data-toggle= "payment-type"]').change(function (e) {
        e.preventDefault();
        var form_id = $(this).data('target');
        $("#"+ form_id).addClass('show-payment-form').siblings().removeClass('show-payment-form');
    });

    // check out page
    $('.delivery-option-btn[data-toggle= "option-btn"]').change(function () {
        var block_id = $(this).data('target');
        $('#'+block_id).addClass('show-option').siblings().removeClass('show-option');
    });

    /*********[ View Cafe Side Menu ]************/
    $("[data-toggle='cafeSideMenu']").on('click', function () {

    });
    /*********[ View Cafe Side Menu ]************/


    /// dashboard foucs on search box
    $('#search-input').on('focus', function () {
        $('#friends-search').addClass('show-content-box').siblings().removeClass('show-content-box');
    });

    $('#search-input').on('focusout', function () {
        $('#friends-message').addClass('show-content-box').siblings().removeClass('show-content-box');
        if ($(this).val() != '') {
            $('#friends-search').addClass('show-content-box').siblings().removeClass('show-content-box');
        }
    });


    /*********[ Customer Dashboard open & close menu ]************/
    $(".customer-dashboard-asidemenu-colapse-btn").on("click", function () {
       $("body").toggleClass("customer-dashboard-asidemenu-colapse");
    });
    $(".customer-dashboard-asidemenu-mobile-btn, .close-customer-dashboard-aside").on("click", function () {
       $("body").toggleClass("open-mobile-customer-dashboard-aside");
    });

    /** Close menu if <= md */
    $(function () {
        if (window.matchMedia('(max-width: 991px)').matches) {
            $(".customerdashboard-body").addClass("customer-dashboard-asidemenu-colapse");
        }
    }());
    /*********[ Customer Dashboard open & close menu ]************/

    /*********[ Customer Dashboard Chat ]************/
    $(".chat-users-aside .friends-message a.mesaage-box,.chat-users-aside .friends-search  a.friend-box, .chat-box .close-chat-btn").on("mousedown", function (e) {
        e.preventDefault();
        $(".chat-box").toggleClass("activeShow");
        $('#search-input').blur();
    });
    /*********[ Customer Dashboard Chat ]************/


    /*********[ Dashboard Menu links on hover on mobile ]************/
    $(".customer-dashboard-asidemenu .customer-menu li .customer-menu-item").hover(function () {
        $(this).parent().find("span").css("top", $(this).offset().top)
    });
    /*********[ Dashboard Menu links on hover on mobile ]************/


    /*********[ perfect Scroll ]************/
    $(".perfect-scroll").each(function () {
        var ps = new PerfectScrollbar(this, {
            suppressScrollX: true
        });
        ps.isRtl = false;
    });
    /*********[ perfect Scroll ]************/

    /*********[ Dashboard header on mobile ]************/
    $(".toggle-customer-dashboard-header").on('click', function (e) {
        e.preventDefault();
        $('body').toggleClass('show-customer-dashboard-header-active');
    });
    /*********[ Dashboard header on mobile ]************/



    /*********[ Review box details ]************/
    $("a.more-details-btn[data-toggle=toggle-review-details]").on('click', function (e) {
        e.preventDefault();
       $(this).closest(".profile-cafe-review").toggleClass('active-full-review');
    });
    /*********[ Review box details ]************/

    // close cafe side menu
    $('#close-cafe-side-menu, .close-cafe-side-menu, .nav-item-back').on('click', function (e) {
        e.preventDefault();
        $('#cafe-side-menu').removeClass('show-cafe-details-side-menu');
        $('body').removeClass('hidden-scroll');
    });

    // open cafe side menu
    $('.view-cafe-sidemenu').on('click',function (e) {
        e.preventDefault();
        $('#cafe-side-menu').addClass('show-cafe-details-side-menu');
        $('body').addClass('hidden-scroll');
    });

    // sort btn toggle
    $('#sort-btn').on('click', function () {
        $('#toggle-sort').toggleClass('show-sort-box');
    });
    $('.fliter-btn').click (function () {
        $('#fliter').addClass('show-popup');
    });

    $('.cuisines-btn').click (function () {
        $('#categories').addClass('show-popup');
    });

    $('.search-result-side-menu-block .close-box').click(function () {
        $(this).parent().removeClass('show-popup');
    });


    /** Smooth Scrolling
     **====================== **/
    $("#cafe_menu_nav a, .scrollLink").on('click', function (e) {
        var className = $(this).attr("href");
        if (className.charAt(0) === "#") {
            e.preventDefault();
            var hash = this.hash,
                scrollTopOffset = $(hash).offset().top;
            $('html, body').animate({
                scrollTop: scrollTopOffset
            }, 500);
        }
    });
    /** => End Smooth Scrolling */


    /** Menu Category Fixed
     **====================== **/
    var cafePageMenuCategoryFixed = function () {
      var cafeMenuCategory = $("#cafe_menu_nav");

      if (cafeMenuCategory.length > 0) {
            cafeMenuPosition = cafeMenuCategory.offset(),
            windowScrollTop = $(window).scrollTop();
          // console.log(cafeMenuPosition);
          // console.log(cafeMenuPosition.top - windowScrollTop);
      }
    };

    /** => End Menu Category Fixed */

    /*********************** [ On Window Scroll ] ***********************/
    $(window).on("scroll", function () {
        cafePageMenuCategoryFixed ();
    });
    /*********************** [ On Window Scroll ] ***********************/

    /*********************** [ main counter ] ***********************/
    $(".main-counter").each(function () {
        var plus = $(this).find(".plus"),
            mins = $(this).find(".mins"),
            num = $(this).find(".num span"),
            num_input = $(this).find(".num input");

        plus.on('click', function () {
            var countVal = parseInt(num_input.val());
            if (countVal < 99) {
                countVal++;
            }

            num.html(countVal);
            num_input.val(countVal);
        });

        mins.on('click', function () {
            var countVal = parseInt(num_input.val());
            if (countVal > 1) {
                countVal--;
            }
            num.html(countVal);
            num_input.val(countVal);
        })
    });
    /*********************** [ main counter ] ***********************/


    /*********************** [ Cart Dropdown ] ***********************/
    $("#cartDropdown").on("click", function () {
        $(".cart-dropdown").toggleClass("show");
    });

    $('#close_cart_menu, #cartDropdown').on('click', function (event) {
        $(this).closest(".cart-dropdown").toggleClass('show');
    });
    /*********************** [ Cart Dropdown ] ***********************/


    /*********************** [ Delete Order Item ] ***********************/
    $(".cart-delete-row").on("click", function () {
        $(this).closest('tr').remove();
    });

    $(".cart-details .trash").on("click", function (e) {
        e.preventDefault();
       $(this).closest("li").remove();
    });
    $(".cart-title .trash").on("click", function (e) {
        e.preventDefault();
       $(this).closest(".cafe-cart").find(".cart-details").remove();
    });
    /*********************** [ Delete Order Item ] ***********************/

    /*********************** [ Selectize Plugin ] ***********************/
    var SelectizeOptoins = {
        create: false,
        copyClassesToDropdown: true,
    };
    $('select').each(function () {
        if (!$(this).hasClass('destory-selectize')) {
            $(this).selectize(SelectizeOptoins);
        }
    });
    /*********************** [ Selectize Plugin ] ***********************/

    /*********************** [ Handle Social Media ] ***********************/

    $("#addNewSocial").on("click", function (e) {
        e.preventDefault();
        var socialRow = `<div class="link-item">
                          <input class="input" type="text" placeholder="Social Media Link">
                          <select class="input select" name="select-time" placeholder="Social Media">
                            <option value="">Social Media</option>
                            <option value="1">Facebook</option>
                            <option value="2">Twitter</option>
                            <option value="3">Youtube</option>
                            <option value="4">Linked in</option>
                            <option value="5">Instagram</option>
                          </select><a class="delete" href="#"><i class="fas fa-times"></i></a>
                        </div>`;
        $("#socialLinks").append(socialRow).find("select").selectize(SelectizeOptoins);
    });

    $(document).on("click", "#socialLinks .delete", function () {
       $(this).closest(".link-item").remove();
    });
    /*********************** [ Handle Social Media ] ***********************/

    /*********************** [ DatePicker ] ***********************/
    $( "#datepicker" ).datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: 'MM d, yy'
    });
    /*********************** [ DatePicker ] ***********************/

    /*********************** [ Selectize Gender ] ***********************/
    $('#select-gender').selectize({
        render: {
            option: function(data, escape) {
                var imgPath = "images/male.svg";
                if (data.value ==="female")
                    imgPath = "images/female.svg";
                return '<div class="option">' +
                    '<div class="icon"><img src='+imgPath+'></div>' +
                    '<span class="label">' + escape(data.text) + '</span>' +
                    '</div>';
            },
            item: function(data, escape) {
                var imgPath = "images/male.svg";
                if (data.value ==="female")
                    imgPath = "images/female.svg";
                return '<div class="item gender-item">' + '<div class="icon"><img src='+imgPath+'></div><div class="label">' + escape(data.text) + '</div></div>';
            }
        },
        create: function(input) {
            return {
                id: 0,
                title: input,
                url: '#'
            };
        }
    });
    $('#select-links').next().find('div.selectize-input > input').prop('disabled', 'disabled');
    /*********************** [ Selectize Gender ] ***********************/


    /*********************** [ handle Rating ] ***********************/
    var starsContaner = $(".stars");
    var starItem = $(".stars > li");
    var handleRating = function (self) {
        self.parent().find("i").removeClass("fas").addClass("far");
        self.prevAll().find("i").removeClass("far").addClass("fas");
        self.find("i").removeClass("far").addClass("fas");
    };

    starItem.on("click", function () {
        var self = $(this);
        var rate = $(this).find('i').data('value');
        self.parent().parent().find('input').val(rate)
    });
    starItem.on("mouseenter", function () {
        handleRating($(this));
    });
    starsContaner.on("mouseleave", function () {
        var rateValue = $(this).parent().find('input').val();
        $(this).find('i').removeClass("fas").addClass("far");
        if (rateValue) {
            $(this).find('i[data-value='+rateValue+']').parent().prevAll().find("i").removeClass("far").addClass("fas");
            $(this).find('i[data-value='+rateValue+']').removeClass("far").addClass("fas");
        }
    });
    /*********************** [ handle Rating ] ***********************/

    // Swal.fire(
    //     'Order Registered',
    //     'Please Wait your order',
    //     'success'
    // );

    // Swal.fire(
    //     'The Internet?',
    //     'That thing is still around?',
    //     'question'
    // )

    // Swal.fire({
    //     title: 'Are you sure?',
    //     text: "You won't be able to revert this!",
    //     type: 'warning',
    //     showCancelButton: true,
    //     confirmButtonColor: '#3085d6',
    //     cancelButtonColor: '#d33',
    //     confirmButtonText: 'Yes, delete it!'
    // }).then((result) => {
    //     if (result.value) {
    //         Swal.fire(
    //             'Deleted!',
    //             'Your file has been deleted.',
    //             'success'
    //         )
    //     }
    // })


    // lost people photo slider
    const lostPeopleSlider = new Swiper('.photo-box-slider', {
            slidesPerView: 1,
            loop: true,
            navigation: {
                nextEl: '.lost-people-btn-prev',
                prevEl: '.lost-people-btn-next',
            },
            observer: true,
            observeParents: true,
            observerUpdate:true,
        });

          setTimeout(function () {
           lostPeopleSlider.update();
          }, 500);



    // multi upload photo to lost people

    //var x = document.getElementById("#input-file").multiple;
    //document.getElementById(".uploaded-photos").text = x;
    $('#input-file').change(function(e){
        var fileName = e.target.files[0].name;
        var files = $('#input-file').prop("files")
        var names = $.map(files, function(val) { return val.name; });
        $('.uploaded-photos').text(names);
        console.log(names);
    });


});
