def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def free(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if pursuer:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if free(nx, ny) and (nx, ny) == (ox, oy):
                return [int(dx), int(dy)]

    resources = observation.get("resources") or []
    best_target = None
    if resources:
        rx, ry = ox, oy
        bestd = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            tx, ty = int(r[0]), int(r[1])
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            d = abs(x - tx) + abs(y - ty)
            if bestd is None or d < bestd or (d == bestd and (tx, ty) < (rx, ry)):
                bestd = d
                best_target = (tx, ty)
        if best_target is None:
            best_target = (ox, oy)
    else:
        best_target = (ox, oy)

    tx, ty = best_target
    best = None
    best_pair = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        risk = abs(nx - ox) + abs(ny - oy)
        pair = (d, -risk, nx, ny)
        if best_pair is None or pair < best_pair:
            best_pair = pair
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]