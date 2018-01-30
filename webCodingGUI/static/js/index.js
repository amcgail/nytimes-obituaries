function fillWith(docs) {
	$(".bodies").html("");
	for( var i in docs ) {
		console.log("WOOP");
		$div = $("<div class='doc'>");
		$div.html( docs[i]['body'] );
		$(".bodies").append($div);
	}

	$(".expandBtn").click( function() {
		$(this).parent().find(".expandDiv").toggle();
	} )
}

function loadMore(num) {
	$.ajax( {
		"method":"GET",
		"url":"/getRandom/" + num,
		"success": function(resp) {
			fillWith( $.parseJSON(resp) );
		}
	} )
}

loadMore(5);