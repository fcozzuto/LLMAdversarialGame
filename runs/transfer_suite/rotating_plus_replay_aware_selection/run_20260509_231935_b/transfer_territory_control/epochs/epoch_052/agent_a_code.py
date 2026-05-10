def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    if w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0)) % 9
    dirs = dirs[t:] + dirs[:t]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if unclaimed:
        # Prefer closer to center, and closer than opponent (roughly).
        target = None
        best = None
        for x, y in unclaimed:
            ds = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            dc = abs(x - cx) + abs(y - cy)
            val = (do - ds) * 5 - dc + (0 if (x, y) in self_terr else 1)
            if best is None or val > best or ((val == best) and (x, y) < target):
                best = val
                target = (x, y)
    else:
        # Otherwise bias toward open space near center but away from opponent territory.
        target = None
        best = None
        for x, y in [(cx, cy), (cx, sy), (sx, cy), ((w - 1) // 2, (h - 1) // 2)]:
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                ds = abs(x - sx) + abs(y - sy)
                do = abs(x - ox) + abs(y - oy)
                val = (do - ds) * 3 - abs(x - cx) - abs(y - cy) - (3 if (x, y) in opp_terr else 0)
                if best is None or val > best:
                    best = val
                    target = (x, y)

    tx, ty = target if target is not None else (cx, cy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Avoid stepping into opponent territory more strongly.
        safety = - (8 if (nx, ny) in opp_terr else 0) - (2 if (nx, ny) in self_terr else 0)
        # Move toward target; also lightly keep distance from opponent.
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        score = safety - d_t + 0.2 * d_o
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]
    return best_move if best_move in ([i, j] for i in (-1, 0, 1) for j in (-1, 0, 1)) else [0, 0]