def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obst = set()
    for c in observation.get("obstacles") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obst.add((int(c[0]), int(c[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    bestd = None

    # Pick move that reduces distance to nearest unclaimed cell (ties broken deterministically).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        if unclaimed:
            dmin = None
            for tx, ty in unclaimed:
                d = abs(tx - nx) + abs(ty - ny)
                if dmin is None or d < dmin:
                    dmin = d
            key = (dmin, dx, dy)
        else:
            # No unclaimed info: move toward center.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            d = abs(cx - nx) + abs(cy - ny)
            key = (d, dx, dy)
        if bestd is None or key < bestd:
            bestd = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]