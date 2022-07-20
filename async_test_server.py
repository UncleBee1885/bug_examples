from machine import Pin, SPI
import network
import rp2
import time
import gc


import uasyncio as asyncio


led = Pin(2, Pin.OUT)
led.value(1)


def w5x00_init():
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20)) #spi,cs,reset pin
    nic.ifconfig(('192.168.1.20','255.255.255.0','192.168.1.1','8.8.8.8'))

    while not nic.isconnected():
        time.sleep(1)
        print(nic.regs())
        
w5x00_init()

html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>%s</p>
    </body>
</html>
"""



async def serve_client(reader, writer):
    print("Client connected")
    request_line = await reader.readline()
    print("Request:", request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass

    request = str(request_line)
    led_on = request.find('/light/on')
    led_off = request.find('/light/off')
    print( 'led on = ' + str(led_on))
    print( 'led off = ' + str(led_off))

    stateis = ""
    if led_on == 6:
        print("led on")
        led.value(1)
        stateis = "LED is ON"

    if led_off == 6:
        print("led off")
        led.value(0)
        stateis = "LED is OFF"

    response = html % stateis
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)

    await writer.drain()
    await writer.wait_closed()
    print("Client disconnected")

async def main():

    
    print('Setting up webserver...')
    
    asyncio.create_task(asyncio.start_server(serve_client, "192.168.1.20", 80))
    while True:

        await asyncio.sleep(5)

def test():
    
    try:
        
        asyncio.run(main())
    except OSError:
        pass
    finally:
        asyncio.run(main())

if __name__ == "__main__":
    test()