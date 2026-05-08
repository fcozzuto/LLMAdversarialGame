def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [w - 1, h - 1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    opp_cells = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    opp_front = set()
    for (x, y) in opp_cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in opp_cells and (nx, ny) not in obstacles:
                    opp_front.add((nx, ny))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    d_to_opp_front = {}
    for c in unclaimed:
        if not c or len(c) < 2: 
            continue
        x, y = int(c[0]), int(c[1])
        if not inb(x, y) or (x, y) in obstacles:
            continue
        if (x, y) in opp_cells:
            continue
        mind = md(x, y, ox, oy)
        if (x, y) in opp_front:
            mind = 0
        d_to_opp_front[(x, y)] = mind

    best = None
    best_key = None
    for (x, y), df in d_to_opp_front.items():
        dself = md(sx, sy, x, y)
        dopp = md(ox, oy, x, y)
        if df > 2 and (x, y) not in opp_front:
            continue
        if dself == 0:
            continue
        # Aggressive denial: prioritize small distance for us, large for opponent, and close-to-front.
        key = (-df, dopp - dself, -dself, x, y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    if best is None:
        # Fallback: move to reduce distance to opponent, but avoid obstacles by axis flipping.
        tx, ty = ox, oy
    else:
        tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) not in obstacles:
        return [dx, dy]
    # Try best alternative deterministically: prefer reducing one axis at a time.
    opts = []
    if dx != 0:
        opts.append((dx, 0))
    if dy != 0:
        opts.append((0, dy))
    if dx != 0 and dy != 0:
        opts.append((dx, 0))
        opts.append((0, dy))
    for adx, ady in opts:
        nx, ny = sx + adx, sy + ady
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [adx, ady]
    return [0, 0]