def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    sx, sy = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    self_role = (observation.get("self_role", "") or "").lower()
    i_am_pursuer = ("purs" in self_role) and ("evad" not in self_role)
    if not ("purs" in self_role or "evad" in self_role):
        i_am_pursuer = True
    if ("purs" in self_role) and ("evad" in self_role):
        i_am_pursuer = True

    obstacles = observation.get("obstacles", [])
    obs_set = set()
    for a, b in obstacles:
        ax, ay = int(a), int(b)
        if 0 <= ax < w and 0 <= ay < h:
            obs_set.add((ax, ay))

    moves = [[dx, dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves.sort(key=lambda m: (m[0], m[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Extra: discourage moves that get "too close" to obstacles (helps vs wall runners)
    def obs_penalty(x, y):
        if (x, y) in obs_set:
            return 10_000_000
        p = 0
        for (oxb, oyb) in ((x+1,y),(x-1,y),(x,y+1),(x,y-1),(x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1)):
            if (oxb, oyb) in obs_set:
                p += 30
        return p

    best = None
    best_score = -10**30 if i_am_pursuer else 10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = dist2(nx, ny, ox, oy)
        pen = obs_penalty(nx, ny)
        # pursuer: minimize distance; evader: maximize distance
        score = (-d - pen) if i_am_pursuer else (d - pen)
        if best is None or (score > best_score if i_am_pursuer else score < best_score):
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]