def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_dist_bias = 0.0
    rem = observation.get("remaining_resource_count", len(resources))
    try:
        rem = int(rem)
    except:
        rem = len(resources)
    if rem <= 6:
        opp_dist_bias = 0.35
    else:
        opp_dist_bias = 0.15

    best = None
    best_score = -10**18
    for (x, y) in resources:
        my_d = cheb(sx, sy, x, y)
        op_d = cheb(ox, oy, x, y)
        contested = 1 if my_d <= op_d else 0
        # Prefer winning/earlier while also pushing away from opponent to reduce their capture next.
        win_margin = (op_d - my_d)
        dist_term = (1.0 / (1 + my_d))
        post_opp = cheb(ox, oy, x, y)
        score = contested * (10.0 * win_margin + 20.0 * dist_term + opp_dist_bias * post_opp)
        if not contested:
            # Still take if it's the least-bad, but with strong penalty.
            score = - (5.0 * (my_d - op_d) + 0.7 * my_d + 0.05 * post_opp)
        if score > best_score:
            best_score = score
            best = (x, y)

    tx, ty = best
    dx_raw = 0 if tx == sx else (1 if tx > sx else -1)
    dy_raw = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(dx_raw, dy_raw), (dx_raw, 0), (0, dy_raw), (dx_raw, -dy_raw), (-dx_raw, dy_raw), (0, 0)]
    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_step = (0, 0)
    best_step_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_away_op = cheb(nx, ny, ox, oy)
        step_score = -d_to + 0.02 * d_away_op
        if step_score > best_step_score:
            best_step_score = step_score
            best_step = (dx, dy)

    dx, dy = best_step
    return [int(dx), int(dy)]