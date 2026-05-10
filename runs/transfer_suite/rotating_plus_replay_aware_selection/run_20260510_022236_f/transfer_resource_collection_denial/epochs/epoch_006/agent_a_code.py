def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose target resource: prefer one we can reach no later than opponent; otherwise nearest to us.
    best = None
    for rx, ry in resources:
        if not inside(rx, ry):
            continue
        dm = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        cand = (dm > do, dm, do, rx, ry)  # (reachable later?, our dist, their dist, tie-break)
        if best is None or cand < best[0]:
            best = (cand, (rx, ry))
    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best[1]

    # Move one step toward target with deterministic tie-breaking; avoid obstacles.
    options = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            options.append((man(nx, ny, tx, ty), man(ox, oy, tx, ty), dx, dy, nx, ny))
    if not options:
        return [0, 0]
    _, _, dx, dy, _, _ = min(options)
    return [int(dx), int(dy)]