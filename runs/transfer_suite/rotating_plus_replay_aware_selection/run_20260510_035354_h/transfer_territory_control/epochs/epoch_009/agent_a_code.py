def choose_move(observation):
    ax, ay = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        try:
            x, y = o
        except:
            x, y = o.get("x"), o.get("y")
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
            obs.add((x, y))
    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for u in unclaimed:
        try:
            x, y = u
        except:
            x, y = u.get("x"), u.get("y")
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
            targets.append((x, y))
    if not targets:
        res = observation.get("resources") or []
        for r in res:
            try:
                x, y = r
            except:
                x, y = r.get("x"), r.get("y")
            if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
                targets.append((x, y))
    if not targets:
        targets = [(w // 2, h // 2)]
    tx, ty = min(targets, key=lambda p: abs(p[0] - ax) + abs(p[1] - ay))
    ox, oy = observation.get("opponent_position", (ax, ay))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        score = (-d_t) + (0.1 * d_o)  # prefer closer to target, slightly farther from opponent
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        for dx, dy in dirs:
            nx, ny = ax + dx, ay + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best