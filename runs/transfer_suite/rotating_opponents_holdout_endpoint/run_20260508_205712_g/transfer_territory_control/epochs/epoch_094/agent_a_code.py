def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    targets = []
    for key in ("resources", "unclaimed_cells", "self_territory", "opponent_territory"):
        if observation.get(key):
            for c in observation.get(key) or []:
                if c and len(c) >= 2:
                    x, y = int(c[0]), int(c[1])
                    if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                        targets.append((x, y))

    if not targets:
        targets = [(ox, oy)]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        dmin = None
        for tx, ty in targets:
            d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            if dmin is None or d < dmin:
                dmin = d

        # Higher is better: prefer smaller distance to targets, also prefer reducing distance to opponent slightly.
        dop = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        score = -(dmin if dmin is not None else 10**9) - 0.01 * dop

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best