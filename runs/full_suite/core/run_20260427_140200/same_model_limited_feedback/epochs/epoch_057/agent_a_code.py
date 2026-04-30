def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    # Build obstacle set
    obs = set()
    for p in obstacles:
        if len(p) >= 2:
            obs.add((p[0], p[1]))
    # Chebyshev distance (diagonal moves allowed)
    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    # Pick best resource: prefer those closer for us than opponent, else the best relative
    if resources:
        best = None
        best_key = None
        for r in resources:
            rx, ry = r[0], r[1]
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # Key: maximize (od - sd), then minimize sd
            key = (-(od - sd), sd, rx, ry)
            if best is None or key < best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        # No resources visible: drift toward center to reduce worst-case
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Obstacle-aware move: choose delta that minimizes distance to target,
    # with tie-breakers that slightly increase distance from opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = max(abs(nx - tx), abs(ny - ty))
        d_opp = max(abs(nx - ox), abs(ny - oy))
        val = (d_to, -d_opp, abs(dx) + abs(dy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    # If all candidate moves invalid, stay
    return [int(best_move[0]), int(best_move[1])]