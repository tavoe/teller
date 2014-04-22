state().loaded(function(){


	document.querySelector(".run-query-button").onclick = function(){
		send_query();
	}


	function send_query(query){
		jQuery.ajax({

			type: "POST",
			url: "query",
			data: query,
			success: receive_query,
			dataType: "json"
		})
	}

	function receive_query(data){
		console.log(data);
	}


});