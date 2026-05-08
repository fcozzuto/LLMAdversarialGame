def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    candidates = observation.get("unclaimed_cells") or []
    target_list = []
    for p in candidates:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y) and (x, y) not in obs:
                target_list.append((x, y))
    if not target_list:
        target_list = []
        opp_t = observation.get("opponent_territory") or []
        for p in opp_t:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                x, y = int(p[0]), int(p[1])
                if in_bounds(x, y) and (x, y) not in obs:
                    target_list.append((x, y))
        if not target_list:
            target_list = [(max(0, min(w - 1, (sx + ox) // 2)), max(0, min(h - 1, (sy + oy) // 2)))]

    def manh(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    # Choose best immediate step toward nearest target; break ties by preferring closer to opponent
    moves = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]
    best = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        d_to_target = min(manh(nx, ny, tx, ty) for tx, ty in target_list)
        d_to_opp = manh(nx, ny, ox, oy)
        key = (d_to_target, d_to_opp, dx, dy)
        if key < best:
            best = key
    dx, dy = best[2], best[3]
    return [int(dx), int(dy)]