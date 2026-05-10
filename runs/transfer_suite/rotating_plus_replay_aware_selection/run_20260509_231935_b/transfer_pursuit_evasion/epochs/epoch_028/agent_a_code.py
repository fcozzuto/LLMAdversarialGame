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
    self_is_pursuer = ("purs" in sr and "evad" in sr) or ("purs" in sr and "evad" not in sr) or ("purs" not in sr and "evad" not in sr and "purs" in orr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            if safe(x + dx, y + dy):
                m += 1
        return m

    best = None
    best_move = [0, 0]
    eps = 1e-6

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        # Pursuer: minimize distance; Evader: maximize distance.
        if self_is_pursuer:
            score = -d + 0.35 * mob + (eps if d == 0 else 0.0)
        else:
            score = d + 0.20 * mob

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]