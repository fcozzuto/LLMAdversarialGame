def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    un = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                un.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = None
    best_key = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if un:
            dmin = 10**9
            for tx, ty in un[:50]:
                d = abs(nx - tx) + abs(ny - ty)
                if d < dmin:
                    dmin = d
            key = (0, dmin, abs(nx - ox) + abs(ny - oy), dx, dy)
        else:
            # fallback: move closer to opponent
            key = (1, abs(nx - ox) + abs(ny - oy), -nx, -ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]