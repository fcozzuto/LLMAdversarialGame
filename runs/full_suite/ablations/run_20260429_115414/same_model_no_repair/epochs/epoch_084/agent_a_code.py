def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a resource where we are closer than the opponent (race objective)
    best_r = None
    best_val = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        # smaller is better: we want my_d significantly less than op_d; small tie-break on my_d
        val = (my_d - op_d) + 0.01 * my_d
        if best_val is None or val < best_val:
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_cost = None
    best_op = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs_set:
            continue
        cost = cheb(nx, ny, tx, ty)
        op_cost = cheb(ox, oy, tx, ty)
        # Prefer moves that make us closer; if tied, prefer moves that also reduce opponent's relative advantage
        rel = (cost - op_cost)
        if best_cost is None or rel < best_cost or (rel == best_cost and (cost < best_op)):
            best_cost = rel
            best_op = cost
            best_move = [dx, dy]

    if best_cost is not None:
        return best_move

    # If all candidate next cells are blocked, allow staying or first non-blocked (deterministic fallback)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) not in obs_set:
            return [dx, dy]
    return [0, 0]