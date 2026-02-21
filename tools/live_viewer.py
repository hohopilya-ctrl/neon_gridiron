import pygame
import socket
import json
import sys

# Simple Pygame Visualizer for Neon Gridiron ULTRA
def run_viewer():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("NEON ULTRA: LIVE VIEWER")
    clock = pygame.time.Clock()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 4243))
    sock.setblocking(False)
    
    data = None
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        try:
            while True: # Drain buffer
                pkt, _ = sock.recvfrom(65535)
                data = json.loads(pkt.decode('utf-8'))
        except: pass
        
        screen.fill((10, 10, 20)) # Dark slate
        
        if data:
            try:
                # Draw Field Border
                pygame.draw.rect(screen, (0, 255, 255), (100, 100, 600, 400), 2)
                
                # Draw Ball
                ball = data.get('ball', {'x': 300, 'y': 200})
                bx, by = ball['x'] + 100, ball['y'] + 100
                pygame.draw.circle(screen, (255, 255, 0), (int(bx), int(by)), 6) # Yellow ball
                
                # Draw Players
                for p in data.get('players', []):
                    team = p.get('team', 0)
                    color = (0, 200, 255) if team == 0 else (255, 50, 150)
                    px, py = p['x'] + 100, p['y'] + 100
                    pygame.draw.circle(screen, color, (int(px), int(py)), 10)
                    
                # Score
                font = pygame.font.SysFont("Arial", 24)
                score = data.get('score', [0, 0])
                time_val = data.get('time', 0.0)
                score_text = font.render(f"SCORE: {score[0]} - {score[1]} | T: {time_val:.1f}", True, (0, 255, 100))
                screen.blit(score_text, (20, 20))
            except Exception as e:
                print(f"Drawing error: {e}")
        else:
            font = pygame.font.SysFont("Arial", 32)
            msg = font.render("WAITING FOR TELEMETRY (PORT 4242)...", True, (255, 255, 255))
            screen.blit(msg, (150, 280))
            
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    run_viewer()
# lines: 55
