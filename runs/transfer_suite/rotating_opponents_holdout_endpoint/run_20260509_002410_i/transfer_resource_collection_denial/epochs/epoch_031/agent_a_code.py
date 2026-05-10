def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0: d1 = -d1
        d2 = y1 - y2
        if d2 < 0: d2 = -d2
        return d1 + d2

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Multi-criteria: pick move that maximizes our capture advantage over opponent for best target,
    # with a slight preference to reduce overall distance to key resources.
    def best_value_from(posx, posy):
        best = None
        for tx, ty in resources:
            myd = man(posx, posy, tx, ty)
            opd = man(ox, oy, tx, ty)
            # larger advantage better; tie-break: smaller myd; then lexicographic target for determinism
            adv = opd - myd
            key = (adv, -myd, tx, ty)
            if best is None or key > best[0]:
                best = (key, myd, adv)
        return best[0]

    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        k = best_value_from(nx, ny)
        # secondary: directly avoid moving away from the currently closest resource (stable behavior)
        closest_my = min(man(nx, ny, rx, ry) for rx, ry in resources)
        # also include tiny preference for moves that reduce our position rank (deterministic)
        tie = (-(closest_my), nx, ny)
        full_key = (k[0], k[1], k[2], k[3], tie)
        if best_key is None or full_key > best_key:
            best_key = full_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]