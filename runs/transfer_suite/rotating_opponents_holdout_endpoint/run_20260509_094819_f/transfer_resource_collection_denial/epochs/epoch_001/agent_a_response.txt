def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        # No resources: drift toward center
        tx, ty = w // 2, h // 2
        best = (10**9, 10**9)
        bd = (0, 0)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if (d, nx, ny) < best:
                best = (d, nx * h + ny)
                bd = (dx, dy)
        return [bd[0], bd[1]]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we're closer to; also prefer those opponent is relatively far from.
        # Deterministic tie-break by coordinates.
        key = (-(od - sd), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    # Greedy step toward target with obstacle avoidance and deterministic tie-breaks
    best_move = (10**9, 10**9, 10**9)
    chosen = (0, 0)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = man(nx, ny, rx, ry)
        # Add mild preference for moves that don't allow opponent to get "strictly" nearer, if contesting
        opp_nd = man(ox, oy, rx, ry)
        # When distances tie, prefer smaller dx,dy lexicographically
        key = (nd, opp_nd - nd, (dx, dy)[0] * 10 + (dx, dy)[1])
        if key < best_move:
            best_move = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]