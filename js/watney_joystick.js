function setupJoystick() {
    return;
    console.log("Creating a joystick...");
    console.log("touchscreen is", VirtualJoystick.touchScreenAvailable() ? "available" : "not available");

    const deadzone = 15;
    let intervalPtr = null;

    var joystick	= new VirtualJoystick({
        container	: document.getElementById('joystickContainer'),
        mouseSupport	: true,
    });

    joystick.addEventListener('touchStart', function(){
        intervalPtr = setInterval(function() {
            const distance = Math.sqrt(Math.pow(joystick.deltaX(), 2) + Math.pow(joystick.deltaY(), 2));
            if (distance <= deadzone) {
                up = false;
                down = false;
                left = false;
                right = false;
                sendKeys();
            }
            else {
                up = joystick.up();
                down = joystick.down();
                left = joystick.left();
                right = joystick.right();
                sendKeys();
            }
        }, 1/30 * 1000);
    });
    joystick.addEventListener('touchEnd', function(){
        clearInterval(intervalPtr);
        up = false;
        down = false;
        left = false;
        right = false;
        sendKeys();
    });
}