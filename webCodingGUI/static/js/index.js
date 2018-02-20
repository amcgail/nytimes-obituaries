function fillWith(docs) {
	$(".bodies").html("");
	for( var i in docs ) {
		var $doc = $("<div class='doc'>").html(docs[i]['body']);

		var $comments = $(`<form class='comments'>
			<input type='hidden' name='fn' value='`+ docs[i]["fn"] +`'>
			<b>Code:</b> <input name='code'>
			<b>New Vocab:</b> <input name='word'>
		</form>`);
		var $commentSub = $("<button type=button>Add new vocabulary</button>").click( ( function($c) {
			return function() {
				$.ajax({
					type:"POST",
					url:"/addVocab",
					data: $c.serialize(),
					success: function() {
						alert("word successfully added");
						$c.find("input").val("");
					}
				});
			}
		}) ($comments) ) ;
		$comments.append($commentSub);
		$doc.append($comments);

		var $commentRemDiv = $(`<form class='comments'>
			<input type='hidden' name='fn' value='`+ docs[i]["fn"] +`'>
			<b>Code:</b> <input name='code'>
			<b>Bad Vocab:</b> <input name='word'>
		</form>`);
		var $commentRem = $("<button type=button>Remove vocabulary</button>").click( ( function($c) {
			return function() {
				$.ajax({
					type:"POST",
					url:"/delVocab",
					data: $c.serialize(),
					success: function() {
						alert("word successfully marked for removal");
						$c.find("input").val("");
					}
				});
			}
		}) ($commentRemDiv) ) ;
		$commentRemDiv.append($commentRem);
		$doc.append($commentRemDiv);

		var $whichIsCorrect = $(`<form class='comments'>
			<input type='hidden' name='fn' value='`+ docs[i]["fn"] +`'>
			<b>What it's supposed to be:</b> <input name='code'>
		</form>`)
		var $correctSub = $("<button type=button>Mark correct coding</button>").click( ( function($c) {
			return function() {
				$.ajax({
					type:"POST",
					url:"/correctCoding",
					data: $c.serialize(),
					success: function() {
						alert("I got your code");
						$c.find("input").val("");
					}
				})
			}
		}) ($whichIsCorrect) ) ;
		$whichIsCorrect.append( $correctSub);
		$doc.append($whichIsCorrect);

		//var $freeform = $("<textarea>");
		//var $code = $("<div class='")

		$div = $("<div>");
		$div.append(
			$doc
		);
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