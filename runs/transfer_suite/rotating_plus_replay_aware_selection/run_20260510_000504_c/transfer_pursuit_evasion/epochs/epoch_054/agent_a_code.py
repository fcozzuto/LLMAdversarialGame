def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("evad" in opponent_role) or ("hunter" in self_role)

    obs_list = list(obstacles)

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def nearest_obs_dist(x, y):
        if not obs_list:
            return 99
        dmin = 99
        for (bx, by) in obs_list:
            d = abs(x - bx) + abs(y - by)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    break
        return dmin

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = md(nx, ny, ox, oy)
        nd = nearest_obs_dist(nx, ny)
        # Deterministic tie-breaking uses (nx, ny)
        if is_pursuer:
            val = (-d) + 0.35 * nd + 0.001 * (nx - ny)  # chase while staying obstacle-far
        else:
            val = d + 0.35 * nd - 0.001 * (nx - ny)   # run away while staying obstacle-far
        tiebreak = 1e-6 * (nx * 10 + ny)  # deterministic small bias
        if best is None or val + tiebreak > best:
            best = val + tiebreak
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]