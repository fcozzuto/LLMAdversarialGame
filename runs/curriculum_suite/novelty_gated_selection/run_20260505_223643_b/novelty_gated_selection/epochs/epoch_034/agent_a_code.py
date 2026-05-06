def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        my_best = 10**9
        opp_best = 10**9
        # Consider racing to a resource; prioritize resources where we are relatively closer,
        # but also prefer avoiding the center to counter center-rush.
        local_best = -10**18
        for rx, ry in resources:
            my_t = man(nx, ny, rx, ry)
            opp_t = man(ox, oy, rx, ry)
            rel = opp_t - my_t  # positive => we are closer
            center_bias = abs(rx - cx) + abs(ry - cy)  # prefer edge resources
            # If opponent is already much closer, still allow switch to less contested resources.
            score = (rel * 10) - my_t + (0.3 * center_bias) + (1.0 if rel > 0 else 0.0)
            if score > local_best:
                local_best = score
            if my_t < my_best:
                my_best = my_t
            if opp_t < opp_best:
                opp_best = opp_t

        # If we cannot beat the opponent to anything, pick a move that increases their distance
        # to our chosen "best" target indirectly by moving edge-ward.
        if opp_best <= my_best:
            edge = abs(nx - cx) + abs(ny - cy)
            local_best += 2.0 * edge

        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]