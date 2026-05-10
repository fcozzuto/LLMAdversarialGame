def choose_move(observation):
    w = observation.get('grid_width')
    h = observation.get('grid_height')
    x, y = observation.get('self_position', (0, 0))
    ox, oy = observation.get('opponent_position', (x, y))
    obstacles = observation.get('obstacles', []) or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except Exception:
            pass

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    inb = lambda nx, ny: 0 <= nx < w and 0 <= ny < h

    resources = observation.get('resources', []) or []
    remaining = observation.get('remaining_resource_count', None)
    target = None
    if resources and (remaining is None or remaining > 0):
        best = 10**18
        for r in resources:
            try:
                rx, ry = r[0], r[1]
            except Exception:
                continue
            if (rx, ry) in obs:
                continue
            d = (rx - x) * (rx - x) + (ry - y) * (ry - y)
            if d < best:
                best = d
                target = (rx, ry)
    if target is None:
        target = (ox, oy)

    tx, ty = target
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # Prefer closer to target; if equal, prefer also being farther from opponent (avoid easy reprisal)
        opp_d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = (-d * 10) + opp_d
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]