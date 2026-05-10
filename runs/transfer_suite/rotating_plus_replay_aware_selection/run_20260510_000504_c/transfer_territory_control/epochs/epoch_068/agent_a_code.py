def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    resources = observation.get("resources") or []

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    manh = lambda x1, y1, x2, y2: (x1 - x2 if x1 >= x2 else x2 - x1) + (y1 - y2 if y1 >= y2 else y2 - y1)

    if resources:
        tx, ty = tuple(resources[0])
        bestd = manh(sx, sy, tx, ty)
        for r in resources[1:]:
            x, y = tuple(r)
            d = manh(sx, sy, x, y)
            if d < bestd:
                bestd, tx, ty = d, x, y
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = -manh(nx, ny, tx, ty) - 0.3 * manh(nx, ny, ox, oy)
        if (nx, ny) in unclaimed:
            score += 0.8
        if (nx, ny) in self_terr:
            score += 0.2
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]