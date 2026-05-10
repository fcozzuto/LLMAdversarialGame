def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    resources = [tuple(p) for p in (observation.get("resources") or [])]
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not inside(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    target = None
    if resources:
        bestd = None
        for x, y in resources:
            if not inside(x, y):
                continue
            d = abs(x - sx) + abs(y - sy)
            if bestd is None or d < bestd:
                bestd = d
                target = (x, y)
    if target is None and unclaimed:
        bestd = None
        for x, y in unclaimed:
            if not inside(x, y):
                continue
            d = abs(x - sx) + abs(y - sy)
            if bestd is None or d < bestd:
                bestd = d
                target = (x, y)

    best = None
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if target is not None:
            score = - (abs(target[0] - nx) + abs(target[1] - ny))
        else:
            score = - (abs(ox - nx) + abs(oy - ny))
        if self_t and (nx, ny) not in self_t:
            score += 0.2
        if best is None or score > bestscore:
            bestscore = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]