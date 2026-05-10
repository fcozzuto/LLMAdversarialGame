def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    pursuer = not any(k in role for k in ("evader", "runner", "fugitive"))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def score_cell(x, y):
        d = abs(x - ox) + abs(y - oy)
        # obstacle pressure: stronger for moving next to obstacles (evader) and avoid blocking ourselves (pursuer)
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    adj += 1
        # If target is adjacent to us, staying close is risky; add a mild tie-breaker term
        stay_close = -2 if d <= 1 else 0
        if pursuer:
            # minimize distance
            return d * 10 + adj * 3 + (-stay_close)
        else:
            # maximize distance
            return -d * 10 + adj * 3 + stay_close

    best_s = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        s = score_cell(nx, ny)
        if best_s is None or s < best_s:
            best_s = s
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]