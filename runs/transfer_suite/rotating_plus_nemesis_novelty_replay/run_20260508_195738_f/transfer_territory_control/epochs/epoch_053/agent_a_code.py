def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 1)) or 1
    h = int(observation.get("grid_height", 1)) or 1
    ox, oy = observation.get("opponent_position", [x, y])
    obs_cells = observation.get("obstacles", []) or []
    obs = set()
    for p in obs_cells:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    oppx, oppy = ox, oy
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = -10**18

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        d = man(nx, ny, oppx, oppy)
        adj = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if (ax, ay) in obs:
                    adj += 1
        score = (-d * 10) - adj
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best