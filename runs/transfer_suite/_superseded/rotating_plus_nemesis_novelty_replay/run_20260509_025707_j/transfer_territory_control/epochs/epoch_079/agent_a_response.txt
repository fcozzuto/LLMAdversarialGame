def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    un_set = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    if sx < 0 or sy < 0:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles

    def near_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp_set:
                        return True
        return False

    def near_my(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in my_set:
                        return True
        return False

    def score_cell(x, y):
        # Favor claiming/expanding near us, and attacking opponent-adjacent squares.
        if not safe(x, y):
            return -10**9
        if (x, y) in opp_set:
            s = 200  # flipping on entry is enabled
        else:
            s = 0
        if (x, y) in un_set:
            s += 60 if near_my(x, y) else 20
        if (x, y) in my_set:
            s += 15  # maintain control
        if near_opp(x, y):
            s += 55
        # Prefer reducing distance to border-adjacent unclaimed
        if un_set:
            best = 10**9
            for cx, cy in ((x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy):
                if (cx, cy) in un_set:
                    best = min(best, abs(cx - sx) + abs(cy - sy))
            if best != 10**9:
                s += 30
        # Obstacle proximity penalty
        obs_near = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy and (x + dx, y + dy) in obstacles:
                    obs_near += 1
        s -= 8 * obs_near
        # Gentle center bias for stability
        cx0, cy0 = (w - 1) / 2, (h - 1) / 2
        s -= 0.5 * (abs(x - cx0) + abs(y - cy0))
        return s

    best_move = (0, 0)
    best_s = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        s = score_cell(nx, ny)
        if s > best_s:
            best_s = s
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]