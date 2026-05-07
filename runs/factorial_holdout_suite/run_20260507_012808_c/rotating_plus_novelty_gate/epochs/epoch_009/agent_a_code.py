def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set(map(tuple, obstacles))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a "contested" resource: opponent is closest, tie-break by our closeness and overall count.
    best = None
    best_key = None
    for rx, ry in resources:
        do = cheb(ox, oy, rx, ry)
        ds = cheb(sx, sy, rx, ry)
        key = (do, -ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            val = -10**9
        else:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Estimate if we can beat opponent to the target.
            # Prefer: smaller ds, and larger margin over opponent.
            margin = (do - ds)
            # Also slightly reward moving toward the target while preventing opponent gains.
            opp_to_best_after = min(cheb(nx + (rx - nx), ny + (ry - ny), rx, ry) for rx, ry in resources) if resources else 0
            # opp_to_best_after is just a harmless bias; keep deterministic and bounded:
            opp_bias = -0.01 * cheb(ox, oy, tx, ty)
            val = margin * 100 + (-ds) * 10 + opp_bias + (-0.1 * opp_to_best_after)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move