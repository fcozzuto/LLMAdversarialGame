def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            x, y = int(x), int(y)
            if inb(x, y):
                obs.add((x, y))
        except Exception:
            pass

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    resources = []
    for p in (observation.get("resources") or []):
        try:
            x, y = p
            x, y = int(x), int(y)
            if ok(x, y):
                resources.append((x, y))
        except Exception:
            pass

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    if not resources or not ok(sx, sy):
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_val = -10**18

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Choose move that maximizes being the closer agent to some resource.
        val = -man(nx, ny, ox, oy) * 0.01
        local_best = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            margin = od - sd  # positive => we are closer than opponent
            if margin > 0:
                score = 1000 * margin - sd
            else:
                score = -0.5 * od - 1.0 * sd
            if score > local_best:
                local_best = score
        # Slight preference for reducing distances generally (ties).
        val += local_best - 0.01 * min(man(nx, ny, rx, ry) for rx, ry in resources)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move