$(document).ready(function(){
    $('.collapse').collapse({
toggle: false,
});

    $('#confirm').click(function(event){
    var href = this.href;
    event.preventDefault();
    $('<div></div>').appendTo('body')
    .html('<div><h5>Are you sure you want to remove all members?</h5></div>')
    .dialog({
	modal: true,
	title: 'Unsubsription Confirmation',
	zIndex: 10000,
	autoOpen: true,
	width: 'auto',
	resizable: false,
	buttons: {
		Yes: function () {
			window.location = href;
			$(this).dialog("close");
		},
		No: function () {
			$(this).dialog("close");
		}
	},
	close: function (event, ui) {
		$(this).remove();
	}
     });
    });
});
