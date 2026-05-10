def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    if not targets:
        for p in observation.get("opponent_territory") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))
        if not targets:
            return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = -10**9
    for tx, ty in targets:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        val = (do * 0.45) - (ds * 1.0)
        # mild central bias to reduce being outflanked
        val += -0.02 * (abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2))
        if val > best_val:
            best_val = val
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    pref = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # prioritize moving toward the chosen target; tie-break by staying away from opponent
            ds = md(nx, ny, tx, ty)
            do = md(nx, ny, ox, oy)
            pref.append((ds - 0.25 * do, abs(mx - dx) + abs(my - dy), mx, my))
    pref.sort()
    return [int(pref[0][2]), int(pref[0][3])]