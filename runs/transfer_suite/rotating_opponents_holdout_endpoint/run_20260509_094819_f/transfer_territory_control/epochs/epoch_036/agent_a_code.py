def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = list(observation.get("resources") or [])
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1)]  # deterministic order

    targets = []
    if resources:
        for p in resources:
            try:
                x, y = int(p[0]), int(p[1])
            except Exception:
                continue
            if inb(x, y) and not blocked(x, y):
                targets.append((x, y))
    elif uncla:
        targets = [p for p in uncla if inb(p[0], p[1]) and not blocked(p[0], p[1])]

    if targets:
        tx, ty = min(targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        best = None
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            # Prefer reducing distance to target; slightly prefer moving away from opponent (avoid fights).
            v = (abs(tx - nx) + abs(ty - ny), -(abs(ox - nx) + abs(oy - ny)), dx, dy)
            if bestv is None or v < bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]

    # No targets known: move to increase distance from opponent deterministically.
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = abs(ox - nx) + abs(oy - ny)
        v = (-d, dx, dy)  # maximize d
        if bestv is None or v < bestv:
            bestv, best = v, [dx, dy]
    return best if best is not None else [0, 0]