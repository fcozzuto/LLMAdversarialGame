def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target that we can reach earlier (or at least with the best race advantage)
    best_key = None
    tx = ty = resources[0][0]
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        edge_pen = (rx in (0, w - 1)) + (ry in (0, h - 1))
        # Smaller ds is good; if tied, prefer larger adv and safer interior
        key = (adv, -ds, -edge_pen, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            tx, ty = rx, ry

    # Obstacle-aware greedy step toward the chosen target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # primary: minimize distance to target
        d = man(nx, ny, tx, ty)
        # secondary: keep race advantage high estimate after move
        est_ds = d
        est_do = man(ox, oy, tx, ty)
        adv = est_do - est_ds
        # tertiary: prefer moves that make us more likely to continue (reduce distance; avoid edges)
        edge_pen = (nx in (0, w - 1)) + (ny in (0, h - 1))
        key = (adv, -d, -edge_pen, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]