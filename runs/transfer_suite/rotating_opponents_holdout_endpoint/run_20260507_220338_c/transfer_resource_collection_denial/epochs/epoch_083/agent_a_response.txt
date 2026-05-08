def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    # Candidate moves (deterministic order)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obst:
            continue

        # Value from next position: prioritize winning resources (opp closer -> bad),
        # then prefer smaller self distance; add small bias to approach opponent late.
        best_for_next = None
        for rx, ry in res:
            sd = man((nx, ny), (rx, ry))
            od = man((ox, oy), (rx, ry))
            # Advantage: positive means we are closer
            adv = od - sd
            # Prefer immediate progress and denying opponent swings
            val = (adv, -sd, rx, ry, -man((nx, ny), (ox, oy)))
            if best_for_next is None or val > best_for_next:
                best_for_next = val
        if best_for_next is None:
            continue

        if best_val is None or best_for_next > best_val:
            best_val = best_for_next
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]