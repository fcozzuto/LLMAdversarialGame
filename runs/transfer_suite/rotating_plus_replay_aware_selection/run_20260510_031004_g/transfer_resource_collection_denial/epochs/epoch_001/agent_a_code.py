def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    sx, sy = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def d2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Pick a target resource that we can reach earlier (or at least not later).
    best = None
    for rx, ry in resources:
        rx = int(rx)
        ry = int(ry)
        myd = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        # Prefer resources where my distance is smaller; break ties by closer and then coordinates.
        key = (myd - opd, myd, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_delta = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        val = (d2(nx, ny, tx, ty), abs((nx - tx)) + abs((ny - ty)), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_delta = [dx, dy]

    return best_delta