def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource biased toward being closer than the opponent
    best_r = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Lower is better: strongly prefer resources we're closer to
        val = 3 * ds - 2 * do + 0.1 * (ds + do)
        if best_val is None or val < best_val:
            best_val = val
            best_r = (rx, ry)

    # If no resources, move to maximize distance from opponent while avoiding obstacles
    if best_r is None:
        target = None
    else:
        target = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if target is not None:
            rx, ry = target
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Choose move that improves our approach and discourages letting opponent be too close
            score = d_self + 0.6 * max(0, d_opp - d_self)
            # Small tie-break: keep away from obstacles-adjacent positions and from opponent overall
            score += 0.01 * cheb(nx, ny, ox, oy)
        else:
            # No target: maximize distance from opponent
            score = -cheb(nx, ny, ox, oy)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]