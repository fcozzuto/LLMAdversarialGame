def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Pick deterministic closest resource (tie-break lexicographically)
    best_r = None
    best_d = None
    for r in resources:
        d = dist2((sx, sy), r)
        if best_r is None or d < best_d or (d == best_d and (r[0], r[1]) < (best_r[0], best_r[1])):
            best_r, best_d = r, d

    tx, ty = best_r
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = dist2((nx, ny), (tx, ty))
        d_to_opp = dist2((nx, ny), (ox, oy))
        # Prefer getting closer to target; break ties by moving away from opponent; then deterministic by delta order
        key = (d_to_target, -d_to_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]