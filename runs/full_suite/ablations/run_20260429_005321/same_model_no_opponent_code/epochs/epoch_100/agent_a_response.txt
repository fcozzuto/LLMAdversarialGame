def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax + ay

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if inside(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        best = None
        bestd = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd, best = d, (dx, dy)
        return [int(best[0]), int(best[1])]

    best_res = None
    best_val = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        closer = do - ds  # higher means we are closer than opponent
        # secondary: prefer resources that are not too far, and discourage giving opponent a head start
        val = closer * 10 - ds
        if best_val is None or val > best_val or (val == best_val and (rx + ry) < (best_res[0] + best_res[1])):
            best_val = val
            best_res = (rx, ry)

    rx, ry = best_res
    # Prefer reducing our distance; if tie, avoid stepping into squares that are closer for opponent to that resource.
    best = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds_new = man(nx, ny, rx, ry)
        opp_adv = man(ox, oy, rx, ry) - man(ox, oy, rx, ry)  # always 0, keep deterministic baseline
        opp_dist_new = man(ox, oy, rx, ry)
        score = (ds_new, -opp_adv, opp_dist_new, (nx + ny))
        # Lower score[0] first; then deterministic tie-breaking by coordinates sum.
        if best_score is None or score < best_score:
            best_score, best = score, (dx, dy)

    return [int(best[0]), int(best[1])]