def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    if ("purs" in sr and "evad" in sr) or (("purs" in sr) and ("evad" not in sr)) or (("purs" not in sr) and ("evad" not in sr) and ("purs" in orr)):
        self_is_pursuer = True
    else:
        self_is_pursuer = False

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return in_bounds(x, y) and (x, y) not in obs
    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy
    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            if safe(x + dx, y + dy):
                m += 1
        return m

    best_score = None
    best_move = [0, 0]

    # If non-pursuer, pick an escape direction with slight bias to corner-touching avoidance.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        md = d2(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        # Wall-run / evasion behavior: avoid moves that immediately reduce mobility too much.
        # Pursuer: minimize distance; Evader: maximize distance.
        if self_is_pursuer:
            score = -md + 0.15 * mob
        else:
            score = md + 0.10 * mob

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]