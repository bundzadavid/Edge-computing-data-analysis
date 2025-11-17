import zmq
import logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s",
#     handlers=[
#         logging.FileHandler("debug.log"),
#         logging.StreamHandler()
#     ]
#     )
    
def main():
    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind("tcp://0.0.0.0:5559")
        
        frontend.setsockopt(zmq.SUBSCRIBE, b"")

        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind("tcp://0.0.0.0:5560")

        zmq.device(zmq.FORWARDER, frontend, backend)
    except Exception as e:
        logging.error("Error, bringing down zmq device: {}".format(e))
    finally:
        pass
        frontend.close()
        backend.close()
        context.term()

if __name__ == "__main__":
    main()
