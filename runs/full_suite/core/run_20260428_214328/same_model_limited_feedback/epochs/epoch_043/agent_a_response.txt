def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles", [])
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick target resource: minimize (self distance - small advantage if we are closer than opponent)
    best = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        dsi = dist((sx, sy), (rx, ry))
        doi = dist((ox, oy), (rx, ry))
        key = (dsi - 0.35 * doi, dsi, abs(rx - (w - 1)) + abs(ry - (h - 1)), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_cost = None
    best_opp = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        dnew = dist((nx, ny), (tx, ty))
        dobp = dist((nx, ny), (ox, oy))
        # Prefer closer to target; in ties, keep farther from opponent
        cost = (dnew, -dobp, dx, dy)
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_opp = dobp
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]