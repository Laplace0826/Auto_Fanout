import time
import mcts
from config import SETUP

if __name__ == "__main__":
    
    setup = SETUP()
    setup.read_config(setup.filepath+"/conf/"+setup.target_file)
    
    # Create the initialized state and initialized node
    current_layout = mcts.Layout()
    use_mcts = mcts.MCTS()
    current_layout.case_input()
    current_state = current_layout.state
    
    t_episodes = []
    
    for episode in range(setup.EPISODE):
        current_state = current_layout.state
        action = use_mcts.take_action(current_state)
        
        t_episode_start = time.time()
        print("\n[Episode] %d\n" % episode)

        current_layout.printLayout()
        
        print("\n[Time] Run time of this episode : ", time.time() - t_episode_start)
        t_episodes.append(time.time() - t_episode_start)
    
    print("\n[Time] Total run time  : " + format(sum(t_episodes), '.3f') + " S")
    print("[Time] Average run time of one episode : " + format(float(sum(t_episodes))/setup.EPISODE, '.3f') + " S")
