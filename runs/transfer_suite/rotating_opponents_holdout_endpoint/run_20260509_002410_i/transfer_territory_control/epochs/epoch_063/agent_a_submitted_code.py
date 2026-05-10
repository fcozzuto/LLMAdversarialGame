def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, w - 1, h - 1

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def is_blocked(x, y):
        return (x, y) in obs

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if inside(x, y) and not is_blocked(x, y):
                resources.append((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if inside(x, y) and not is_blocked(x, y):
                unclaimed.append((x, y))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1]])
            except:
                continue
            if inside(x, y):
                oppT.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    target_list = resources if resources else unclaimed
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or is_blocked(nx, ny):
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        if target_list:
            tx, ty = min(target_list, key=lambda t: abs(t[0] - nx) + abs(t[1] - ny))
            d_t = abs(tx - nx) + abs(ty - ny)
        else:
            d_t = abs(nx - (w // 2)) + abs(ny - (h // 2))
        gain = -d_t
        danger = -d_opp
        score = gain + (5 if (nx, ny) in oppT else 0) + danger * 0.05
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score, best = score, (dx, dy)

    return list(best if best is not None else (0, 0))