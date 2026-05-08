def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if resources:
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    curd = abs(tx - sx) + abs(ty - sy)
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        score = (nd, abs(ox - nx) + abs(oy - ny), 0 if (dx, dy) != (0, 0) else 1)
        if best_move is None or score < best_move[0] or (score == best_move[0] and dx < best_move[1][0]):
            best_move = (score, (dx, dy))
    if best_move is None:
        return [0, 0]
    return [best_move[1][0], best_move[1][1]]