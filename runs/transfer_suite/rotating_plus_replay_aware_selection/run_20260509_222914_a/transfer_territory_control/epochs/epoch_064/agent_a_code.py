def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_ter = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_ter.add((x, y))
    opp_ter = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_ter.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))
    candidates = unclaimed if unclaimed else [(sx, sy)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_cell(tx, ty):
        dS = abs(tx - sx) + abs(ty - sy)
        dO = abs(tx - ox) + abs(ty - oy)
        edge = 0
        if (tx, ty) in opp_ter:
            edge -= 5  # avoid giving opponent controlled cells unless advantageous
        if (tx, ty) in self_ter:
            edge += 2  # reinforce existing control
        return (dS, -dO, edge)

    # Prefer quick expansion near current position with safety from opponent
    best = None
    best_key = None
    for (tx, ty) in candidates:
        if abs(tx - sx) > 3 or abs(ty - sy) > 3:
            continue
        if not in_bounds(tx, ty):
            continue
        k = score_cell(tx, ty)
        if best is None or k < best_key:
            best, best_key = (tx, ty), k

    if best is None:
        # fallback: go toward the best among all unclaimed (deterministic)
        for (tx, ty) in candidates:
            if not in_bounds(tx, ty):
                continue
            k = score_cell(tx, ty)
            if best is None or k < best_key:
                best, best_key = (tx, ty), k

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if in_bounds(nx, ny):
        return [dx, dy]

    # If diagonal blocked, try axis moves deterministically toward the target
    options = []
    if dx != 0 and in_bounds(sx + dx, sy):
        options.append((dx, 0))
    if dy != 0 and in_bounds(sx, sy + dy):
        options.append((0, dy))
    if dx != 0 and dy != 0:
        if in_bounds(sx + dx, sy) and in_bounds(sx, sy + dy):
            pass
    if options:
        return list(options[0])

    return [0, 0]