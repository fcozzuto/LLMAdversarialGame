def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obst = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    if not resources:
        return [0, 0]

    # Pick a resource that we can reach relatively sooner than the opponent.
    best_r = None
    best_s = -10**18
    for rx, ry in resources:
        ds = dist2((sx, sy), (rx, ry))
        do = dist2((ox, oy), (rx, ry))
        # Mild obstacle danger: prefer squares where the resource isn't "inside" dense obstacles.
        danger = 0
        for ex, ey in obst:
            d = abs(rx - ex) + abs(ry - ey)
            if d == 0:
                danger += 3.0
            elif d <= 1:
                danger += 1.5
            elif d <= 3:
                danger += 0.3
        s = (do - ds) * 1.0 - danger
        # Tie-break deterministically by position.
        if s > best_s or (s == best_s and (rx, ry) < (best_r[0], best_r[1])):
            best_s = s
            best_r = (rx, ry)

    tx, ty = best_r
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        d_target = dist2((nx, ny), (tx, ty))
        d_opp = dist2((nx, ny), (ox, oy))
        # Obstacle clearance reward
        clear = 0.0
        for ex, ey in obst:
            md = abs(nx - ex) + abs(ny - ey)
            if md == 0:
                clear -= 2.0
            elif md == 1:
                clear -= 0.7
            elif md == 2:
                clear -= 0.25
        v = (-d_target) * 1.2 + d_opp * 0.03 + clear * 0.6
        if v > best_v:
            best_v = v
            best_m = (dx, dy)
        elif v == best_v:
            # deterministic tie-break
            if (dx, dy) < best_m:
                best_m = (dx, dy)
    return [best_m[0], best_m[1]]