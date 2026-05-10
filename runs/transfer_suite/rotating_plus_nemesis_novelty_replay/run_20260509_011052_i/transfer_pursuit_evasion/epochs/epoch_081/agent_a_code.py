def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def nearest_corner(px, py):
        best = corners[0]
        bd = cheb(px, py, best[0], best[1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if d < bd:
                bd, best = d, (cx, cy)
        return best

    def farthest_corner(px, py):
        best = corners[0]
        bd = cheb(px, py, best[0], best[1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if d > bd:
                bd, best = d, (cx, cy)
        return best

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target_corner = nearest_corner(ox, oy)
    other_corner = farthest_corner(ox, oy)

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_to_op = cheb(nx, ny, ox, oy)

        # Intercept: race toward the opponent's nearest corner, but also deny by checking the farthest corner.
        d_corner_me = cheb(nx, ny, target_corner[0], target_corner[1])
        d_corner_op = cheb(ox, oy, target_corner[0], target_corner[1])

        # If I'm already as close or closer to the corner than the opponent, prioritize direct pursuit.
        intercept_gain = (d_corner_op - d_corner_me)

        # Evasion counterpart: maximize separation and drift to farthest corner.
        d_corner_other = cheb(nx, ny, other_corner[0], other_corner[1])
        if is_pursuer:
            val = d_to_op * 2.0 - intercept_gain * 1.5 - d_corner_other * 0.05
        else:
            val = -d_to_op * 2.0 + d_corner_other * 1.2 + (-intercept_gain) * 0.2

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]