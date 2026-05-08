def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = str(observation.get("self_role", "")).lower()
    my_is_pursuer = ("pursur" in self_role) or (self_role == "pursuer")

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        return (nx, ny) if inside(nx, ny) else (x, y)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if my_is_pursuer:
        target = (ox, oy)
        bestv = None
        bestm = [0, 0]
        for dx, dy in cand:
            nx, ny = step(sx, sy, dx, dy)
            v = -man((nx, ny), target)
            # tie-break: slightly prefer moves that reduce x then y (deterministic)
            v2 = v - 0.001 * (abs(nx - ox) + abs(ny - oy)) - 0.00001 * (dx * 3 + dy)
            if bestv is None or v2 > bestv:
                bestv = v2
                bestm = [dx, dy]
        return bestm
    else:
        # Evader: run toward the farthest corner from opponent, while not stepping into obstacles.
        tx, ty = max(corners, key=lambda c: man(c, (ox, oy)))
        bestv = None
        bestm = [0, 0]
        for dx, dy in cand:
            nx, ny = step(sx, sy, dx, dy)
            d_corner = man((nx, ny), (tx, ty))
            d_opp = man((nx, ny), (ox, oy))
            # prioritize maximizing distance to opponent, then distance from our current corner target
            v = (d_opp * 2.0) + (d_corner * 0.2) - 0.01 * (abs(nx - tx) + abs(ny - ty))
            if bestv is None or v > bestv or (v == bestv and [dx, dy] < bestm):
                bestv = v
                bestm = [dx, dy]
        return bestm