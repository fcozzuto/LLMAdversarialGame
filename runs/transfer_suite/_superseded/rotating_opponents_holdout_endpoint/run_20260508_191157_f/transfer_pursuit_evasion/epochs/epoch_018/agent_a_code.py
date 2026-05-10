def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obset.add((p[0], p[1]))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obset

    role = observation.get("self_role", "pursuer")
    env = observation.get("environment_name", "pursuit_evasion")
    if env != "pursuit_evasion":
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    def score(nx, ny):
        d = cheb(nx, ny, ox, oy)
        # Prefer not moving into "crowded" obstacle-adjacent squares (wall runner opponent).
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obset:
                    adj_obs += 1
        # Deterministic tie-breaks via coordinates.
        tie = -(nx * 17 + ny * 31)

        if role == "pursuer":
            # maximize capture chances: minimize distance, but avoid obstacles.
            return (-d) * 100 + (12 - adj_obs) + tie
        else:
            # evader: maximize distance, but avoid obstacles and border preference.
            border_pen = 0
            if nx == 0 or nx == w - 1:
                border_pen += 2
            if ny == 0 or ny == h - 1:
                border_pen += 2
            return (d) * 100 + (12 - adj_obs) - border_pen + tie

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = score(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]