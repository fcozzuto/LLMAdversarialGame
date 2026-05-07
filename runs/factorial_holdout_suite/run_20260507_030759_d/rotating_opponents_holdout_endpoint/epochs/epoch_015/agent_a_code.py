def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                oset.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and (x, y) not in oset:
                res_list.append((x, y))

    if not res_list:
        # Fallback: move to increase distance from opponent while not stepping into obstacles
        best = (-(10**9), 0, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in oset:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if (d, -abs(nx - ox) - abs(ny - oy)) > (best[0], best[1]):
                best = (d, 0, (dx, dy))
        return list(best[2])

    def score_cell(x, y):
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        # Prefer being closer than opponent; penalize if opponent is much closer.
        margin = (od - sd)
        # Small bias for cells that move toward opposite side of opponent's sweep tendencies.
        sweep_bias = 0
        if y == oy:
            sweep_bias += 1.5
        if x == ox:
            sweep_bias += 1.5
        # Prefer nearer overall, but only after margin.
        return (margin * 10) - sd + sweep_bias

    # Choose target resource that maximizes our advantage
    target = max(res_list, key=lambda c: (score_cell(c[0], c[1]), -(abs(c[0] - sx) + abs(c[1] - sy))))
    tx, ty = target

    best_move = (-(10**18), (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        # Prefer immediate collection; otherwise improve target advantage.
        if (nx, ny) == (tx, ty):
            sc = 10**12
        else:
            sd2 = abs(tx - nx) + abs(ty - ny)
            od2 = abs(tx - ox) + abs(ty - oy)
            margin2 = od2 - sd2
            # Avoid moving into positions adjacent to obstacles too often.
            adj_obs = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    ax, ay = nx + adx, ny + ady
                    if (ax, ay) in oset:
                        adj_obs += 1
            sc = margin2 * 10 - sd2 - 0.1 * adj_obs
            # If opponent is on same row/col, slightly prefer blocking their next step direction.
            if nx == ox or ny == oy:
                sc += 0.25 * (abs(nx - ox) + abs(ny - oy))
        if sc > best_move[0]:
            best_move = (sc, (dx, dy))

    return [best_move[1][0], best_move[1][1]]