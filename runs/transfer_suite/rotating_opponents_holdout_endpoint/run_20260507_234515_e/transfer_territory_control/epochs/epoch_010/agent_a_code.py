def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    def safe(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    unclaimed = observation.get("unclaimed_cells", []) or []
    targets = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))

    if not targets:
        res = observation.get("resources", []) or []
        for p in res:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))

    if not targets:
        op = observation.get("opponent_position", None)
        if isinstance(op, (list, tuple)) and len(op) >= 2:
            tx, ty = int(op[0]), int(op[1])
        else:
            tx, ty = sx, sy
    else:
        targets.sort(key=lambda c: (man(sx, sy, c[0], c[1]), c[1], c[0]))
        tx, ty = targets[0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    bestd = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        if d < bestd:
            bestd = d
            best = (dx, dy)
    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]