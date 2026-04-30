def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick a target resource where we are (relatively) closer than the opponent.
    best_r = resources[0]
    best_r_key = None
    for r in resources:
        rx, ry = r
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        # Higher is better: how much closer we are than opponent; tie-break by being closer to it.
        key = (op_d - my_d, -(my_d), -(rx + ry))
        if best_r_key is None or key > best_r_key:
            best_r_key = key
            best_r = r

    rx, ry = best_r
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d_new = cheb(nx, ny, rx, ry)
        op_d_to_target = cheb(ox, oy, rx, ry)
        # Also try not to step into the opponent's immediate "line": maximize distance to opponent.
        opp_dist = cheb(nx, ny, ox, oy)
        # Primary: increase advantage on the target; Secondary: be closer; Tertiary: keep away from opponent.
        key = (op_d_to_target - my_d_new, -my_d_new, opp_dist)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]