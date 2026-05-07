def choose_move(observation):
    w = int(observation.get("grid_width") or 0)
    h = int(observation.get("grid_height") or 0)
    if w <= 0: w = 8
    if h <= 0: h = 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step_options():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    yield dx, dy

    opts = list(step_options())
    if not opts:
        return [0, 0]

    best = None
    best_score = -10**18
    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        # Prefer moving toward nearest resource; slight preference to reduce distance to opponent if needed
        if resources:
            mind = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < mind:
                    mind = d
            score = -mind * 10 + (abs(nx - ox) + abs(ny - oy)) * 1
        else:
            # No visible resources: head toward center lane while keeping away from opponent
            center = (w - 1) // 2
            target_x = 0 if sx <= center else w - 1
            target_y = (h - 1) // 2
            score = - (abs(nx - target_x) + abs(ny - target_y)) * 3 + (abs(nx - ox) + abs(ny - oy)) * 2
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]