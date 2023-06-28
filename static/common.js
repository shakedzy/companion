$(document).ready(function(){
    setInterval(function () {
      $.get("/check_server_errors", function (response) {
          var server_errors = response['server_errors'];
          server_errors.forEach(showNotification)
      });
    }, 3000);
})


function showNotification(message) {
  // Create notification div
  var notification = document.createElement('div');
  notification.className = 'notification';
  notification.innerHTML = message;

  // Create close button
  var closeButton = document.createElement('button');
  closeButton.type = 'button';
  closeButton.className = 'close';
  closeButton.innerHTML = '&times;';

  // Add event listener to close button
  closeButton.addEventListener('click', function() {
    notification.remove();
  });

  // Add close button to notification
  notification.appendChild(closeButton);

  // Add notification to notification area
  var notificationArea = document.getElementById('notification-area');
  notificationArea.appendChild(notification);

  // Remove notification after 3 seconds
  setTimeout(function() {
    notification.remove();
  }, 5000);
}