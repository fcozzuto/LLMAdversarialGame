def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If standing on a resource, take it.
    if (x, y) in set(tuple(r) for r in resources):
        return [0, 0]

    # Choose the resource that maximizes our lead over opponent (opp_dist - self_dist).
    # If no lead possible, choose the resource that minimizes our distance.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # larger is better
        key = (lead, -ds, -rx, -ry)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy
    else:
        tx, ty = best_r

    # Greedy step toward (tx,ty) while avoiding obstacles and penalizing moves that increase our distance.
    best_move = (0, 0)
    best_score = None
    cur_d = cheb(x, y, tx, ty)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Encourage improving our distance; discourage giving opponent a larger lead by moving away.
        # Also slightly prefer moves that get us closer to the opponent's target regions (shrink both distances).
        opp_d = cheb(ox, oy, tx, ty)
        score = (cur_d - nd, -nd, -(opp_d), -(abs(nx - ox) + abs(ny - oy)), -((nx + ny) % 3))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]