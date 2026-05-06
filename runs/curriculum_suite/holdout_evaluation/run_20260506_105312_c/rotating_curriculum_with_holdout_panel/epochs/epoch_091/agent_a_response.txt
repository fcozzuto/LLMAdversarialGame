def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                rlist.append((rx, ry))
    if not rlist:
        # Safety: stay away from opponent
        best = None
        for dx, dy, nx, ny in cand:
            d = abs(nx - ox) + abs(ny - oy)
            key = (d, -abs(dx) - abs(dy), dx, dy)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    def eval_next(nx, ny):
        best_rel = -10**9
        best_prog = 10**9
        for rx, ry in rlist:
            my_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            rel = opp_d - my_d  # higher => more ahead vs opponent on that resource
            if rel > best_rel or (rel == best_rel and my_d < best_prog):
                best_rel = rel
                best_prog = my_d
        # Also gently prefer decreasing distance to the best resource we can contest
        return (best_rel, -best_prog, -(abs(nx - ox) + abs(ny - oy)))

    best_key = None
    best_move = [0, 0]
    for dx, dy, nx, ny in cand:
        key = eval_next(nx, ny)
        # deterministic tie-break
        tieb = (-abs(dx), -abs(dy), dx, dy)
        full = (key, tieb)
        if best_key is None or full > best_key:
            best_key = full
            best_move = [dx, dy]
    return best_move