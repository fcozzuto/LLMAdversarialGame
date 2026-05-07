def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def cheb(ax, ay, bx, by):
        d1 = abs(bx - ax)
        d2 = abs(by - ay)
        return d1 if d1 >= d2 else d2

    # Pick a "safe" target: we can reach no later than opponent.
    best_t = None
    best_ts = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        st = cheb(sx, sy, rx, ry)
        ot = cheb(ox, oy, rx, ry)
        if st > ot:
            continue
        # Prefer larger time advantage, then shorter own time, then higher resource coordinate value.
        ts = (ot - st) * 100000 - st * 1000 + (rx + ry) * 3
        if ts > best_ts or (ts == best_ts and (rx, ry) < best_t):
            best_ts = ts
            best_t = (rx, ry)

    # If no safe target, take the resource that minimizes opponent lead (still deterministic).
    if best_t is None:
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = cheb(sx, sy, rx, ry)
            ot = cheb(ox, oy, rx, ry)
            diff = ot - st
            ts = diff * 100000 - st * 600 + (rx + ry) * 3  # favors less negative diff (smaller opponent lead)
            if ts > best_ts or (ts == best_ts and (rx, ry) < best_t):
                best_ts = ts
                best_t = (rx, ry)

    rx, ry = best_t

    # Move greedily toward the target, but only among legal adjacent cells; break ties by improving time advantage.
    best_m = (0, 0)
    best_ms = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        st = cheb(nx, ny, rx, ry)
        ot = cheb(ox, oy, rx, ry)
        # Strongly prefer smaller st; then prefer better matchup (ot-st).
        ms = -st * 100000 + (ot - st) * 20000 + (nx + ny) * 0.01
        if ms > best_ms:
            best_ms = ms
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]