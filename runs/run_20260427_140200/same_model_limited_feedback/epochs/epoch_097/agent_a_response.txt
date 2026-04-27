def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Choose a resource where we are relatively closer than the opponent
    best = None
    best_key = -10**18
    for r in resources:
        ds = dist2((sx, sy), r)
        do = dist2((ox, oy), r)
        key = (do - ds)  # larger means we're closer
        if key > best_key:
            best_key = key
            best = r

    tx, ty = best
    opp_target = None
    opp_best = -10**18
    for r in resources:
        do = dist2((ox, oy), r)
        ds = dist2((sx, sy), r)
        key = (ds - do)
        if key > opp_best:
            opp_best = key
            opp_target = r

    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            # Prefer not to move into obstacles (engine may keep us in place)
            score = -10**12
        else:
            # Primary: get to our chosen target quickly
            d_self = dist2((nx, ny), (tx, ty))
            d_curr = dist2((sx, sy), (tx, ty))
            prog = d_curr - d_self  # positive if closer
            # Secondary: increase distance from opponent to avoid contests
            d_op = dist2((nx, ny), (ox, oy))
            d_op_curr = dist2((sx, sy), (ox, oy))
            keep = d_op - d_op_curr
            # Tertiary: disrupt opponent's likely target (make them farther)
            d_opp_next = dist2((ox, oy), opp_target)
            d_opp_curr = d_opp_next
            # If our move brings us closer to their target, it can help them; penalize
            contam = 0
            if opp_target is not None:
                contam = -max(0, dist2((nx, ny), opp_target) - dist2((sx, sy), opp_target))
            score = 3.0 * prog + 0.6 * keep + 0.1 * d_op + 0.2 * contam

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]