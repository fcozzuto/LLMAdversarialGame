def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    # Pick resource where we are relatively closer than opponent.
    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer winning contests; then closer.
        key = (do - ds, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else (sx, sy)

    # Choose a valid step minimizing distance to target; break ties by moving away from opponent.
    best_move = (0, 0)
    best_score = None
    best_opp = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        score = (d_to, -d_opp, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
            best_opp = d_opp

    return [int(best_move[0]), int(best_move[1])]