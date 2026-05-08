def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    sx, sy = self_pos[0], self_pos[1]
    ox, oy = opp_pos[0], opp_pos[1]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal allowed)

    if not resources:
        return [0, 0]

    # If we're on a resource, stay to collect it.
    if tuple(self_pos) in set(tuple(p) for p in resources):
        return [0, 0]

    best = None
    best_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer resources where we are closer than opponent; break ties by smaller self distance.
        val = (od - sd) * 1000 - sd
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    dx = tx - sx
    dy = ty - sy
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

    candidates = []
    # Main step toward target
    candidates.append((step_x, step_y))
    # Also consider single-axis move toward target to avoid obstacles
    if step_x != 0:
        candidates.append((step_x, 0))
    if step_y != 0:
        candidates.append((0, step_y))
    # And no move / fallback diagonals
    candidates.append((0, 0))
    if step_x != 0 or step_y != 0:
        candidates.append((step_x, 0))
        candidates.append((0, step_y))

    best_move = (0, 0)
    best_score = -10**18
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if (nx, ny) in obstacles:
            continue
        # Score candidate: prefer reducing our distance to target, and not letting opponent get too close.
        nd = dist((nx, ny), (tx, ty))
        nod = dist((ox, oy), (tx, ty))
        # tie-break: prefer moves that also reduce opponent-to-target gap
        score = (best_val) - nd * 10 - max(0, nd - (nod)) * 50
        if score > best_score:
            best_score = score
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]