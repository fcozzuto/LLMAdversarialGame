def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is None:
            continue
        if isinstance(p, dict):
            x = p.get("x", p.get(0, None))
            y = p.get("y", p.get(1, None))
        else:
            x, y = p[0], p[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def neighbor_options(px, py):
        c = 0
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if safe(nx, ny):
                c += 1
        return c

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)  # prefer staying away from edges
        options = neighbor_options(nx, ny)
        # maximize survival pressure: far from pursuer, away from edges, and with mobility
        key = (dist, edge, options)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best