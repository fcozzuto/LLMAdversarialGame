def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def near_obs_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and (xx, yy) in obstacles:
                    pen += 2
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_score = None
    # Evaluate each move by (primary) reduce our distance to the best resource overall, (secondary) steal resources
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        my_dist_min = 10**9
        opp_dist_min = 10**9
        steal_diff = 10**9
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            if d_my < my_dist_min:
                my_dist_min = d_my
            d_op = cheb(ox, oy, rx, ry)
            if d_op < opp_dist_min:
                opp_dist_min = d_op
            # Prefer states where we're closer than opponent to some resource
            diff = d_my - d_op
            if diff < steal_diff:
                steal_diff = diff

        # Obstacle/edge pressure: prefer moves that keep mobility
        mobility = 0
        for mdx, mdy in moves:
            xx, yy = nx + mdx, ny + mdy
            if valid(xx, yy):
                mobility += 1

        pen = near_obs_pen(nx, ny)
        # Primary: be fast to resources; Secondary: improve steal_diff; Tertiary: mobility; Penalty: obstacle adjacency
        score = (my_dist_min, steal_diff, -mobility, pen)
        if best_score is None or score < best_score:
            best_score = score
            best = [dxm, dym]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]