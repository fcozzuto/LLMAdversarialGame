def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for c in (observation.get("obstacles", []) or []):
        try:
            x, y = c
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))
    unclaimed_set = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    if unclaimed_set:
        target = min(unclaimed_set, key=lambda p: (man(p, (sx, sy)), man(p, (ox, oy))))
    elif opp_set:
        target = min(opp_set, key=lambda p: (man(p, (sx, sy)), -man(p, (ox, oy))))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        val = 0

        # Territory interaction weights
        if cell in opp_set:
            val += 500  # immediate swing
            val += 3 * man(cell, (ox, oy)) * 0  # deterministic no-op to keep simple
        elif cell in unclaimed_set:
            val += 80
        elif cell in self_set:
            val += 20
        else:
            val += 5

        # Center drift
        val += 10 * (-(abs(nx - cx) + abs(ny - cy)))

        # If there is a target, bias toward it
        if target is not None:
            val += 6 * (-(man(cell, target)))

        # Separation from opponent (territory counterclaim style)
        val += 2 * (man(cell, (ox, oy)))

        # Prefer staying only if equal-ish
        if dx == 0 and dy == 0:
            val -= 1

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move