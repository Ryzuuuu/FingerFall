import cv2, mediapipe as mp, random, time, urllib.request, os
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision

MODEL = "hand_landmarker.task"
if not os.path.exists(MODEL):
    print("Downloading hand model (~10MB)...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        MODEL)

detector = vision.HandLandmarker.create_from_options(
    vision.HandLandmarkerOptions(
        base_options=mpp.BaseOptions(model_asset_path=MODEL), num_hands=1))

cap = cv2.VideoCapture(0)

def new_ball(w, h):
    return {'x': random.randint(40, w-40), 'y': 0, 'r': 35,
            'speed': random.randint(10, 20),
            'color': tuple(random.randint(80, 255) for _ in range(3))}

def new_bomb(w, h):
    return {'x': random.randint(40, w-40), 'y': 0, 'r': 30,
            'speed': random.randint(6, 11)}

def reset():
    return [], [], 0, time.time(), time.time(), False

balls, bombs, score, last_spawn, last_bomb, game_over = reset()

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]

    # --- GAME OVER SCREEN ---
    if game_over:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        cv2.putText(frame, 'GAME OVER', (w//2-185, h//2-60), cv2.FONT_HERSHEY_SIMPLEX, 2,   (0,60,255), 6)
        cv2.putText(frame, f'Score: {score}',  (w//2-110, h//2),    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255,255,255), 3)
        cv2.putText(frame, 'R - Restart   Q - Quit', (w//2-185, h//2+65), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200,200,200), 2)
        cv2.imshow('Ball Game', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            balls, bombs, score, last_spawn, last_bomb, game_over = reset()
        elif key == ord('q'):
            break
        continue

    # --- SPAWN ---
    now = time.time()
    if now - last_spawn > 1.2:
        balls.append(new_ball(w, h))
        last_spawn = now
    if now - last_bomb > 3.0:
        bombs.append(new_bomb(w, h))
        last_bomb = now

    # --- HAND DETECTION ---
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                      data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    res = detector.detect(mp_img)
    fx = fy = -1
    if res.hand_landmarks:
        lm = res.hand_landmarks[0][8]
        fx, fy = int(lm.x * w), int(lm.y * h)
        cv2.circle(frame, (fx, fy), 18, (0, 255, 100), -1)

    # --- BALLS ---
    alive = []
    for b in balls:
        b['y'] += b['speed']
        hit = fx != -1 and ((fx-b['x'])**2 + (fy-b['y'])**2)**0.5 < b['r']
        if hit:           score += 10
        elif b['y'] > h: score -= 8
        else:
            cv2.circle(frame, (b['x'], b['y']), b['r'], b['color'], -1)
            cv2.circle(frame, (b['x'], b['y']), b['r'], (255,255,255), 2)
            alive.append(b)
    balls = alive

    # --- BOMBS ---
    live_bombs = []
    for bm in bombs:
        bm['y'] += bm['speed']
        hit = fx != -1 and ((fx-bm['x'])**2 + (fy-bm['y'])**2)**0.5 < bm['r']
        if hit:
            game_over = True
            break
        elif bm['y'] <= h:
            cv2.circle(frame, (bm['x'], bm['y']), bm['r'], (30, 30, 30), -1)
            cv2.circle(frame, (bm['x'], bm['y']), bm['r'], (0, 0, 220), 2)
            off = bm['r'] // 2
            cv2.line(frame, (bm['x']-off, bm['y']-off), (bm['x']+off, bm['y']+off), (0,0,220), 3)
            cv2.line(frame, (bm['x']+off, bm['y']-off), (bm['x']-off, bm['y']+off), (0,0,220), 3)
            live_bombs.append(bm)
    if not game_over:
        bombs = live_bombs

    # --- HUD ---
    col = (0, 255, 100) if score >= 0 else (0, 80, 255)
    cv2.putText(frame, f'Score: {score}', (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0,0,0), 5)
    cv2.putText(frame, f'Score: {score}', (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.4, col, 3)
    cv2.putText(frame, '+10 ball   -2 miss   X = BOMB = dead   Q quit', (10, h-15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)

    cv2.imshow('Ball Game', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()