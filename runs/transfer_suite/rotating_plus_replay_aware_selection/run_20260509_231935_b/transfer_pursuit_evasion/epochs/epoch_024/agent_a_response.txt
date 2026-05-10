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

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            if safe(x + dx, y + dy):
                c += 1
        return c

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)

        # Obstacle-aware nudge: discourage stepping into positions that tightly constrain movement.
        # (For both roles, higher mobility is generally better; pursuer wants approach, evader wants escape.)
        if self_is_pursuer:
            score = (-dist, -mob, abs(nx - ox), abs(ny - oy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            score = (dist, mob, -abs(nx - ox), -abs(ny - oy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move