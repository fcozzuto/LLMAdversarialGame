def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    self_cells = set(tuple(p) for p in observation.get("self_territory", []) or [])
    opp_cells = set(tuple(p) for p in observation.get("opponent_territory", []) or [])
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []) or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    resources = observation.get("resources", None) or []
    if resources:
        targets = [tuple(p) for p in resources]
    elif unclaimed:
        targets = list(unclaimed)
    else:
        targets = [(w // 2, h // 2)]

    best = None
    best_sc = -10**18
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    opp_adj_pen = 0
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Choose deterministic target by nearest; break ties by reading order
        tx, ty = None, None
        bd = 10**18
        for (a, b) in targets:
            d = man(nx, ny, a, b)
            if d < bd or (d == bd and (a, b) < (tx, ty) if tx is not None else True):
                bd = d
                tx, ty = a, b
        sc = -bd + 0.5 * man(nx, ny, ox, oy)
        if (nx, ny) in self_cells:
            sc += 2.0
        if (nx, ny) in opp_cells:
            sc -= 5.0
        if unclaimed and (nx, ny) in unclaimed:
            sc += 1.0
        # Slightly discourage stepping next to opponent
        if man(nx, ny, ox, oy) == 1:
            opp_adj_pen = -1.0
        else:
            opp_adj_pen = 0.0
        sc += opp_adj_pen
        # deterministic tie-break
        if sc > best_sc or (sc == best_sc and best is not None and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]