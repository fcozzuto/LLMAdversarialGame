def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Resource-denial: pick the resource that is currently best for the opponent,
    # but where we can become relatively closer (opp_dist - our_dist).
    best_target = None
    best_key = None
    for rx, ry in resources:
        opp_d = cheb(ox, oy, rx, ry)
        our_d = cheb(sx, sy, rx, ry)
        # Prefer targets that opponent can reach quickly and we can contest.
        # Key: maximize opp_d - our_d; tie-break by smaller opp_d, then by position.
        key = (-(opp_d - our_d), opp_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    opp_d_target = cheb(ox, oy, rx, ry)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        our_d_new = cheb(nx, ny, rx, ry)
        # Primary: maximize contest advantage (opponent distance - our distance).
        # Secondary: keep moving closer to target.
        # Tertiary: slight preference to reduce distance to opponent (intercept pressure).
        val = (opp_d_target - our_d_new) * 1000 - our_d_new * 5 - cheb(nx, ny, ox, oy)
        # Micro-stall avoidance: don't keep still if another legal move improves our_d_new.
        if dx == 0 and dy == 0:
            val -= 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]