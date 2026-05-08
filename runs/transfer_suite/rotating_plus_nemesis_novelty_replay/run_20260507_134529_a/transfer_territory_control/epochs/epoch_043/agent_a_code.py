def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def to_points(key):
        pts = []
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    pts.append((x, y))
        return pts

    targets = to_points("unclaimed_cells")
    if not targets:
        targets = to_points("resources")
    if not targets:
        opp = to_points("opponent_territory")
        targets = opp if opp else [(ox, oy)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    def mindist(x, y, pts):
        md = None
        for tx, ty in pts:
            d = abs(tx - x) + abs(ty - y)
            if md is None or d < md:
                md = d
        return md if md is not None else 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = mindist(nx, ny, targets)
        d_o = abs(nx - ox) + abs(ny - oy)
        score = (d_t, d_o, dx, dy)  # minimize
        if best is None or score < best:
            best = score
            best_move = [dx, dy]

    return best_move if (0 <= sx + best_move[0] < w and 0 <= sy + best_move[1] < h and (sx + best_move[0], sy + best_move[1]) not in obstacles) else [0, 0]