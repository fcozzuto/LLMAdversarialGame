def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for grid+diagonals

    # Pick a resource where we are relatively closer than opponent (contest), otherwise pick a good fallback.
    best = None
    best_val = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist((x, y), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Value: strong preference to where opponent is farther; also break ties by smaller self distance.
        val = (od - sd) * 10 - sd
        # Slightly prefer moving away from opponent when contesting is poor (strategic change).
        val += -dist((x, y), (ox, oy))
        if val > best_val:
            best_val = val
            best = (rx, ry)

    # If no resources, move to increase distance from opponent and avoid obstacles.
    if best is None:
        tx, ty = ox, oy
        want = None
        best_val = -10**9
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
                continue
            v = dist((nx, ny), (tx, ty)) - 0.1 * (abs(dx) + abs(dy))
            if v > best_val:
                best_val = v
                want = (dx, dy)
        return list(want if want is not None else (0, 0))

    tx, ty = best

    # Greedy step toward target; if blocked, choose next-best that still improves or preserves distance.
    cur_d = dist((x, y), (tx, ty))
    chosen = None
    chosen_d = cur_d + 1
    chosen_op = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        od = dist((nx, ny), (ox, oy))
        # Prefer reducing target distance; if equal, prefer staying further from opponent.
        if nd < chosen_d or (nd == chosen_d and od > (chosen_op if chosen_op is not None else -10**9)):
            chosen_d = nd
            chosen = (dx, dy)
            chosen_op = od

    return list(chosen if chosen is not None else (0, 0))