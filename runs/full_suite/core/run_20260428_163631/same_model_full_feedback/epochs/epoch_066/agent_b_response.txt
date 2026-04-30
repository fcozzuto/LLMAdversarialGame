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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp_now = cheb(nx, ny, ox, oy)

        if resources:
            # Choose a target that we can reach earlier than the opponent.
            best_gap = -10**18
            best_d = 10**18
            for rx, ry in resources:
                d_us = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                gap = d_op - d_us  # higher means we are closer
                if gap > best_gap or (gap == best_gap and d_us < best_d):
                    best_gap = gap
                    best_d = d_us

            if best_gap > 0:
                target_score = 80 * best_gap - 3 * best_d
            else:
                # If we can't win any race, go for our closest resource.
                target_score = -2 * best_d
        else:
            target_score = 0

        # Keep some distance from opponent while not sacrificing target progress.
        opp_score = -15 * (7 - d_opp_now if d_opp_now < 7 else 0)
        obst_score = -2 * adj_obst(nx, ny)

        val = target_score + opp_score + obst_score
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]