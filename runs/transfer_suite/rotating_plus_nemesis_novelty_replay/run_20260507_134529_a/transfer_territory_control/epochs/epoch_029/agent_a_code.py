def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    targets = unclaimed
    if not targets:
        targets = to_set("resources")

    best = (10**9, 10**9, 10**9)
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Penalize stepping into opponent territory; otherwise chase nearest target.
        step_pen = 1 if (nx, ny) in opp_terr else 0
        if targets:
            dist = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in targets)
        else:
            dist = 0
        # Secondary objective: keep some distance from opponent.
        opp_dist = abs(nx - ox) + abs(ny - oy)
        cand = (step_pen, dist, -opp_dist)
        if cand < best:
            best = cand
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]