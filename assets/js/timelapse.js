 function sendPostSignal(url, postData,onSuccess) {
			$.ajax({
	        type: "POST",
	        //the url where you want to sent the userName and password to
	        url: url,
	        dataType: 'json',
	        async: false,
	        //json object to sent to the authentication url
	        data: postData,
	        success: onSuccess  
    		});
    }
    function checkStatus() {
    		$.post('./active', null,
    				function (dataReceive) {
				        if (dataReceive.active) {
				  			$('#status').html(dataReceive.message + ' last image on ' + dataReceive.params.lastPictureTime);
				  			var seconds = dataReceive.params.seconds;
				  			var hours = Math.floor(seconds / 3600);
				  			seconds = seconds % 3600;
				  			var minutes = Math.floor(seconds / 60);
				  			seconds = seconds % 60;
				  			$('#secondsField').val(seconds).prop('disabled', true);
				  			$('#minutesField').val(minutes).prop('disabled', true);
				  			$('#hoursField').val(hours).prop('disabled', true);
				  			$('#widthField').prop('disabled', true);
				  			$('#heightField').prop('disabled', true);
				  			$('#project').val(dataReceive.params.project).prop('disabled', true);
				  			
				  			$('#samplePic').attr("src","./samplePic.jpeg?" + new Date().getTime() );
				  		}
				  		else {
				  			$('#status').html(dataReceive.message);
				  			$('#secondsField').prop('disabled', false);
				  			$('#minutesField').prop('disabled', false);
				  			$('#hoursField').prop('disabled', false);
				  			$('#widthField').prop('disabled', false);
				  			$('#heightField').prop('disabled', false);
				  			$('#project').prop('disabled', false);
				  		}
	    			});
            };
            
    function getVideoDevices(){
    	$.post('./getVideoDevices', null,
    				function (dataReceive) {
    					if (dataReceive.length == 0 ) {
    						$('#videDeviceList').hide();
    						alert('no video devide found');
    					}
    					else{
						for (x in dataReceive)	{
							var newOption = $("<option></option>").attr("value",dataReceive[x]).text(dataReceive[x])
							newOption.appendTo($('#videDeviceList')); 
						}
    							$('#videDeviceList').show();
    						if (dataReceive.length == 1) {
    							$('#videDeviceList').attr("disabled", "disabled");
    						}
    					}
    				
	    			});
            };
    function takePic(){
    	$.post('./samplePic', null,
    				function (dataReceive) {
    					$('#samplePic').attr("src","./samplePic.jpeg?" + new Date().getTime() );
	    			});
            };
    function projectList(){
    	$.post('./projectList', null,
    				function (dataReceive) {
					$('#projectList').empty()
					for (x in dataReceive.list)
					  {
						var newOption = $("<option></option>").attr("value",dataReceive.list[x].name).text(dataReceive.list[x].name).attr("data-outputFilePath", dataReceive.list[x].outputFilePath).attr("data-firstImageFileName", dataReceive.list[x].firstImageFileName)
						newOption.appendTo($('#projectList')); 
						if ($('#projectList').val() == dataReceive.list[x].name) {
							newOption.attr("selected","selected")	;
						}
						//newOption.data('outputFilePath', dataReceive.list[x].outputFilePath);
					  }
    					
	    			});
            };
    function stopTimeLapse(){
    	$.post('./stop', 
    				function (dataReceive) {
    					$('#status').html('stopping');;
	    			});
            }; 
            
    function makeMovie(){
    	$('#createMoviePreLoader').show();
    	$('#movieLink').hide();
       	var dataToSend = { 'project': $('#projectList').find('option:selected').val(), 'imageWidth':  $('#widthField').val(), 'imageHeight' : $('#heightField').val(), 'fps' :$('#fps').val()}
    	$.post('./createMovie', dataToSend,
    				function (dataReceive) {
    					$('#createMoviePreLoader').hide();
    					$('#movieLink').attr("href",dataReceive.movieFileName);
    					$('#movieLink').show();
	    			});
            };

    function startTimeLapse(){
    	var seconds = parseFloat($('#hoursField').val()) * 3600 + parseFloat($('#minutesField').val())*60 + parseFloat($('#secondsField').val());
    	var dataToSend = {'seconds':seconds, 'project': $('#project').val(), 'imageWidth':  $('#widthField').val(), 'imageHeight' : $('#heightField').val()}
    	$.post('./start', dataToSend,
    				function (dataReceive) {
    					$('#status').html('starting timelapse');
	    			});
            };      
            
    checkStatus();
    window.setInterval(function(){
	   checkStatus();
	}, 5000);

	$('a[data-toggle="tab"]').on('shown', function (e) {
		if ( e.target.hash == "#movie") { projectList();};
	})


$("#projectList").change(function () {
  
	var selected = $(this).find('option:selected');

	var outputFileName= selected.data('outputfilepath')
	if (outputFileName)
		{
			$('#movieLink').attr("href",outputFileName);
			$('#movieLink').show();
		}
		else {
			$('#movieLink').hide();
		}
	var firstImageFileName= selected.data('firstimagefilename')
	if (firstImageFileName)
		{
			$('#firstImage').attr("src",firstImageFileName );
			$('#firstImage').show();
		}
		else {
			$('#firstImage').hide();
		}

	

  }).trigger('change');
	
  getVideoDevices();
