def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = observation.get("resources", []) or []
    res_list = []
    for r in resources:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
            res_list.append((x, y))
        elif r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            res_list.append((x, y))
    res_list = [(x, y) for (x, y) in res_list if 0 <= x < w and 0 <= y < h and (x, y) not in blocked]

    target = None
    if res_list:
        best = None
        for x, y in res_list:
            d = abs(x - sx) + abs(y - sy)
            if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
                best = (d, (x, y))
        target = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        if target is None:
            score = d_opp
        else:
            tx, ty = target
            d_tar = abs(nx - tx) + abs(ny - ty)
            score = -d_tar * 10 + d_opp
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]