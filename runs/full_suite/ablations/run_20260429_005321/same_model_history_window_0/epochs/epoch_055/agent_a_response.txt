def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Target: nearest resource to us; break ties by also being closer than opponent.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        d1 = dist2(sx, sy, rx, ry)
        d2 = dist2(ox, oy, rx, ry)
        cand = (d1, d2, abs(rx - sx) + abs(ry - sy), rx, ry)
        if best is None or cand < best[0]:
            best = (cand, rx, ry)
    _, tx, ty = best[0], best[1], best[2]

    # Preferred step: move one toward target.
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx0, sy + dy0
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
        return [dx0, dy0]

    # Otherwise, choose among valid moves that reduce our distance; tie-break by also blocking opponent.
    best_move = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obs:
            continue
        d_self = dist2(nx, ny, tx, ty)
        d_opp = dist2(ox, oy, tx, ty)
        # Tie-break: prefer moves that make us relatively closer than opponent.
        rel = abs(d_self) - abs(d_opp)
        cand = (d_self, rel, dist2(nx, ny, ox, oy), dx, dy)
        if cand < best_move:
            best_move = cand
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]