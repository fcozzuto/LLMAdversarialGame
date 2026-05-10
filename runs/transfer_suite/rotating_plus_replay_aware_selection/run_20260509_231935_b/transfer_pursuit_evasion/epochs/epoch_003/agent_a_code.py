def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = observation.get("obstacles", []) or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    # In pursuit_evasion, if opponent is evader then we are pursuer (max points on capture).
    am_evader = ("evad" in sr)
    if not am_evader and ("evad" in orr):
        am_evader = False
    elif am_evader and ("evad" in orr):
        am_evader = True

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def free_adj(nx, ny):
        cnt = 0
        for dx, dy in deltas:
            tx = clamp(nx + dx, 0, w - 1)
            ty = clamp(ny + dy, 0, h - 1)
            if (tx, ty) not in obs:
                cnt += 1
        return cnt

    best_move = [0, 0]
    if am_evader:
        best_val = None  # maximize
        for dx, dy in deltas:
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obs:
                continue
            if nx == ox and ny == oy:
                continue
            dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            # Prefer moving away, and if similar, keep options open.
            val = (dist2, free_adj(nx, ny), -abs(nx - (w - 1 if ox < w/2 else 0)) - abs(ny - (h - 1 if oy < h/2 else 0)))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        best_val = None  # minimize distance; tie-breaker prefer higher free_adj
        for dx, dy in deltas:
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obs:
                continue
            dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            # Tie-breakers: reduce Chebyshev distance first, then keep mobility.
            cheb = max(abs(nx - ox), abs(ny - oy))
            val = (dist2, cheb, -free_adj(nx, ny), 0 if (nx == ox and ny == oy) else 1)
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]