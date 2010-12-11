jQuery(document).ready(function(){

	$("fieldset.optional").each(function(){
		$fieldset = $(this);
		var legend = $fieldset.find("legend").text();
		if( $fieldset.find(".errorlist").length == 0 ) {
			$fieldset.after('<a class="toggleFieldset" rel="' + $fieldset.attr("id") + '">' + legend + '</a>').hide();
		}
	});
	
	$("fieldset.optional legend").live('click', function(){
	    $fieldset = $(this).parent("fieldset");
	    legend = $fieldset.find("legend").text();
	    $fieldset.after('<a class="toggleFieldset" rel="' + $fieldset.attr("id") + '">' + legend + '</a>').fadeOut('fast');
	});

	$("a.toggleFieldset").live('click', function(){
		var id = $(this).attr("rel");
		$("fieldset#" + id).fadeIn();
		$(this).remove();
	});

});
