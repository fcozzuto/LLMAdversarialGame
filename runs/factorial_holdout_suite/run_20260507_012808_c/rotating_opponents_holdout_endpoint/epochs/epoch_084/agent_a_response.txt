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

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds
        edge_pen = (rx in (0, w - 1)) + (ry in (0, h - 1))
        key = (adv, -ds, -edge_pen, -rx, -ry)
        if best_key is None or key > best_key:
            best_key, best_r = key, (rx, ry)

    rx, ry = best_r
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                ns = man(nx, ny, rx, ry)
                no = man(ox, oy, rx, ry)
                key = (no - ns, -ns, -((nx in (0, w - 1)) + (ny in (0, h - 1))), -dx, -dy)
                moves.append((key, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0], reverse=True)
    return [int(moves[0][1]), int(moves[0][2])]