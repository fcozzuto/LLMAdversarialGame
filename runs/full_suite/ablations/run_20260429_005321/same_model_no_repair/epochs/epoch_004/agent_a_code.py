def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score_resource(rx, ry):
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        # Prefer resources we can reach first; otherwise pick ones where we're not too far behind.
        return (0 if sd <= od else 1, od - sd, sd, -rx, -ry)

    target = None
    best = None
    for r in resources:
        k = score_resource(r[0], r[1])
        if best is None or k < best:
            best = k
            target = (r[0], r[1])

    if target is None:
        return [0, 0]
    tx, ty = target

    def step_toward(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy

    preferred = step_toward(sx, sy, tx, ty)

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd2 = man((nx, ny), (tx, ty))
        od2 = man((ox, oy), (tx, ty))
        my_lead = sd2 - od2
        # Primary: move that keeps/achieves being at least as good as opponent; Secondary: get closer to target.
        # Also discourage stepping away from opponent capture race by penalizing increasing distance to opponent.
        d_opp_now = man((sx, sy), (ox, oy))
        d_opp_next = man((nx, ny), (ox, oy))
        key = (0 if my_lead <= 0 else 1, abs(my_lead), sd2, d_opp_next - d_opp_now, 0 if (dx, dy) == preferred else 1, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]