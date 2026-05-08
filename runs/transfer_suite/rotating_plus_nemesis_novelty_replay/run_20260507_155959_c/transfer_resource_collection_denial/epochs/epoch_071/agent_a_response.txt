def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    res_list = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res_list.append((x, y))

    if not res_list:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            cand = (d, abs(dx) + abs(dy), dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[2], best[3]]

    best_move = None
    best_score = None
    opp_pos = (ox, oy)

    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        our_pos = (nx, ny)
        best_val = None
        for r in res_list:
            d_our = md(our_pos, r)
            d_opp = md(opp_pos, r)
            val = (d_opp - d_our) - 0.01 * d_our  # prefer resources we can reach first
            if best_val is None or val > best_val:
                best_val = val
        # If no move yields positive lead, just grab nearest resource deterministically
        if best_val is None:
            best_val = -1e9
        if best_score is None or (best_val, -abs(dx) - abs(dy), -nx, -ny) > (best_score[0], best_score[1], best_score[2], best_score[3]):
            best_score = (best_val, -abs(dx) - abs(dy), -nx, -ny)
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]