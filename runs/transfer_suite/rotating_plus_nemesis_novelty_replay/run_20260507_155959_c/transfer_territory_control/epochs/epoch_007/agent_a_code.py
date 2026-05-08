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

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_center = None
    if opp_cells:
        sx2 = sum(x for x, _ in opp_cells)
        sy2 = sum(y for _, y in opp_cells)
        n = len(opp_cells)
        opp_center = (sx2 // n, sy2 // n)
    else:
        opp_center = (ox, oy)

    def pick_target():
        if not unclaimed:
            return None
        best = None
        bestk = None
        for x, y in unclaimed:
            if (x, y) in obstacles or not inb(x, y):
                continue
            ds = dist(sx, sy, x, y)
            do = dist(opp_center[0], opp_center[1], x, y)
            # Reachable and relatively safe from opponent; deterministic tie-breakers
            k = (do - ds * 0.9, y, x)
            if bestk is None or k < bestk:
                bestk = k
                best = (x, y)
        return best

    target = pick_target()
    if target is None:
        # Push toward opponent center; slight preference to approach along x then y
        tx, ty = opp_center
    else:
        tx, ty = target

    best_move = (0, 0)
    best_val = None

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep in place; mirror that deterministically

        cell = (nx, ny)
        v = 0.0

        if cell in unclaimed:
            v += 6.0
        if cell in self_cells:
            v += 1.0
        if cell in opp_cells:
            # Entry flips control; value depends on proximity to opponent territory leader area
            v += 3.0 - dist(opp_center[0], opp_center[1], nx, ny) * 0.05

        # Main drive: reduce distance to target
        v += -dist(nx, ny, tx, ty) * 0.35
        # Secondary: avoid immediate contact with opponent center unless capturing unclaimed/opp
        v += dist(nx, ny, opp_center[0], opp_center[1]) * 0.05

        if best_val is None or v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]