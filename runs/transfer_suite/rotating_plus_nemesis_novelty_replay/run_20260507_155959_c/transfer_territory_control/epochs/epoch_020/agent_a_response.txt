def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = [tuple(xy) for xy in (observation.get("unclaimed_cells", []) or [])]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_center = (ox, oy)
    if opp_cells:
        sx2 = sum(x for x, _ in opp_cells)
        sy2 = sum(y for _, y in opp_cells)
        n = len(opp_cells) or 1
        opp_center = (sx2 // n, sy2 // n)

    # choose a target: prefer unclaimed closer to us but on the opponent side,
    # and slightly prefer near front where opponent territory exists.
    def score_target(tx, ty):
        if (tx, ty) in obstacles or not inb(tx, ty):
            return -10**9
        # "front" heuristic: maximize progress towards opponent center
        prog = (tx - sx) * (opp_center[0] - sx) + (ty - sy) * (opp_center[1] - sy)
        # encourage expansion adjacent to opponent (good for flipping) and ours (avoid isolation)
        adj_opp = 0
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            if (tx + dx, ty + dy) in opp_cells:
                adj_opp += 1
        adj_self = 0
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            if (tx + dx, ty + dy) in self_cells:
                adj_self += 1
        # balance distances
        d_us = abs(tx - sx) + abs(ty - sy)
        d_opp = abs(tx - opp_center[0]) + abs(ty - opp_center[1])
        return 5 * adj_opp + 2 * adj_self + 0.35 * prog - 0.9 * d_us - 0.2 * d_opp

    if not unclaimed:
        return [0, 0]

    best = None
    bestv = -10**18
    for x, y in unclaimed:
        v = score_target(x, y)
        if v > bestv:
            bestv = v
            best = (x, y)

    tx, ty = best

    # move one step to reduce distance to target; allow diagonals; never step into obstacle effectively
    best_move = (0, 0)
    best_dm = 10**9
    best_tieb = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not inb(nx, ny):
            continue
        dm = abs(nx - tx) + abs(ny - ty)
        # if we can step into opponent territory, prioritize it
        step_opp = 1 if (nx, ny) in opp_cells else 0
        # slight preference to progress towards opponent center
        prog = (nx - sx) * (opp_center[0] - sx) + (ny - sy) * (opp_center[1] - sy)
        tieb = 10 * step_opp + 0.01 * prog
        if dm < best_dm or (dm == best_dm and tieb > best_tieb):
            best_dm = dm
            best_tieb = tieb
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]