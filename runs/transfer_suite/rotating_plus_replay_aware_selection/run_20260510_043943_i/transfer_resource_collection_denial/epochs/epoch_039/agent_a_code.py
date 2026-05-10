def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def best_value(nx, ny):
        if not resources:
            # no resources left: drift toward center to reduce collision risk
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dx = abs(nx - cx) + abs(ny - cy)
            od = abs(ox - cx) + abs(oy - cy)
            return (od - dx) * 10 - dx
        best = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # race: win first, then proximity; also prefer not giving opponent advantage
            val = (do - ds) * 1000 - ds - (do // 2)
            if ds == 0:
                val += 10**9
            elif ds == 1:
                val += 10**5
            elif ds == 2:
                val += 10**2
            if do <= ds:
                val -= 50 * (ds - do + 1)
            # slight preference for resources closer to us overall
            val -= 0.1 * (ds)
            if val > best:
                best = val
        return best

    best_move = [0, 0]
    best_val = -10**18
    # deterministic tie-break by deltas order
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        v = best_value(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    # if all moves blocked, stay
    return best_move if isinstance(best_move, list) else [0, 0]