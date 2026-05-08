def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((x, y) for x, y in obstacles_list)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    res_set = set((x, y) for x, y in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    # Choose best target deterministically with opponent-advantage weighting.
    best = None
    best_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; secondary prefer far/near to control tie-break.
        val = (od - sd) * 1000 - sd
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Greedy local move evaluation toward target with obstacle avoidance and slight anti-blocking.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= observation["grid_width"] or ny >= observation["grid_height"]:
            continue
        if (nx, ny) in obstacles:
            continue
        # If stepping onto a resource, prioritize heavily.
        score = 0
        if (nx, ny) in res_set:
            score += 10**9
        # Progress toward target.
        score += cheb(nx, ny, tx, ty) * -10
        # Prefer decreasing our distance to target; also keep away if opponent would steal next.
        score += (cheb(sx, sy, tx, ty) - cheb(nx, ny, tx, ty)) * 50
        # Small preference for moves that don't let opponent become strictly closer next turn.
        opp_next = cheb(ox, oy, tx, ty)
        score += (-1) * max(0, opp_next - cheb(nx, ny, tx, ty)) * 2
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move