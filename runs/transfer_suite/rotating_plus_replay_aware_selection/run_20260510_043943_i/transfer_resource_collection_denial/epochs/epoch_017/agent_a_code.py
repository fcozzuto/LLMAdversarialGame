def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        rx, ry = min((tuple(r) for r in resources), key=lambda rr: (man(ox, oy, rr[0], rr[1]), rr[0], rr[1]))
        tx, ty = rx, ry
    else:
        tx, ty = ox, oy

    best = None
    best_mv = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        sc += -man(nx, ny, tx, ty)  # move toward target
        sc += 0.2 * man(nx, ny, ox, oy)  # avoid opponent a bit
        sc += 0.01 * (nx - ny)  # deterministic tie-break
        if best is None or sc > best:
            best = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]