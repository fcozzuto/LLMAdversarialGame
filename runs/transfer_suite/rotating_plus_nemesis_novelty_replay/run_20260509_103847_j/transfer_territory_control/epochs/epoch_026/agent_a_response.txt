def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Precompute a few closest opponent cells for a cheap "distance-to-op-territory" term
    op_list = list(opT)
    if not op_list:
        op_list = [(ox, oy)]
    op_list.sort(key=lambda p: dist(sx, sy, p[0], p[1]))
    op_list = op_list[:6]

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        if (nx, ny) in opT:
            reward = 70
        elif (nx, ny) in unT:
            reward = 8
        elif (nx, ny) in selfT:
            reward = 2
        else:
            reward = 0

        mind = 10**9
        for tx, ty in op_list:
            d = dist(nx, ny, tx, ty)
            if d < mind:
                mind = d

        # Strongly prefer entering opponent territory; otherwise advance toward it.
        score = reward * 10 - mind * 4 - dist(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best