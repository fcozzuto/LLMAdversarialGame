def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Pick a target resource we can reach earlier than opponent (by distance)
    best = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = (ds - do)  # smaller is better (we are closer)
        # Encourage grabbing resources if opponent is already far
        val += 0.1 * ds
        if best is None or val < best_val:
            best = (rx, ry)
            best_val = val
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Heuristic: minimize distance to target, maximize distance from opponent
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # If stepping onto resource directly is best
        on_res = 1 if (nx, ny) in set(tuple(r) for r in resources) else 0
        score = (d_t * 1.0) - (d_o * 0.08) - (on_res * 1e6)

        # Slightly prefer moves that reduce target distance deterministically
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]