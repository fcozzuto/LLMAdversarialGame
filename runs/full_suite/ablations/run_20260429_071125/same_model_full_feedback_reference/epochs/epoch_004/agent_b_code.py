def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]
    resources = observation.get("resources", []) or []
    obs_in = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_in:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    if not (0 <= sx < w and 0 <= sy < h and w > 0 and h > 0):
        return [0, 0]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    tgt = None
    bestd = 10**9
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if inb(rx, ry):
            d = man((sx, sy), (rx, ry))
            if d < bestd:
                bestd, tgt = d, (rx, ry)
    if tgt is None:
        tgt = (ox, oy)
    cur_dt = man((sx, sy), tgt)
    cur_do = man((sx, sy), (ox, oy))
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dt = man((nx, ny), tgt)
        do = man((nx, ny), (ox, oy))
        toward = cur_dt - dt
        away = do - cur_do
        capture = 20 if (nx, ny) == tgt else 0
        score = toward * 3 + away * 2 + capture
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move