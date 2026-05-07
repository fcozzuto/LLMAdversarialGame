def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best = -10**18
    best_mv = (0, 0)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Pick the best resource to pursue from (nx,ny), scoring how much closer we are than opponent.
        local = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Strongly prefer resources we can reach no later than opponent.
            diff = od - sd  # positive => we closer
            sc = diff * 1000 - sd * 3
            if diff >= 0:
                sc += 5000
            local = sc if sc > local else local

        # Secondary: avoid positions that give opponent near-term access to any resource.
        opp_pressure = 10**9
        for rx, ry in resources:
            opp_pressure = min(opp_pressure, man(ox, oy, rx, ry) - man(nx, ny, rx, ry))
        # Small tie-break toward continuing motion if not worse.
        move_pen = 0 if (dx == 0 and dy == 0) else -2

        total = local + opp_pressure * 2 + move_pen
        if total > best:
            best = total
            best_mv = (dx, dy)

    dx, dy = best_mv
    nx, ny = sx + dx, sy + dy
    return [dx, dy] if valid(nx, ny) else [0, 0]