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
    self_is_pursuer = ("purs" in sr) and ("evad" not in sr)
    if not ("purs" in sr or "evad" in sr) and ("purs" in orr):
        self_is_pursuer = False
    if ("evad" in sr) and ("purs" not in sr):
        self_is_pursuer = False
    if ("purs" in sr) and ("evad" in sr):
        self_is_pursuer = True

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        # If pursuer: minimize distance; if evader: maximize distance.
        score = d if not self_is_pursuer else -d

        # Small deterministic obstacle/escape preference: favor moves that increase local freedom.
        freedom = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if safe(tx, ty):
                freedom += 1
        score += (freedom * 0.01 if self_is_pursuer else -freedom * 0.01)

        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return best