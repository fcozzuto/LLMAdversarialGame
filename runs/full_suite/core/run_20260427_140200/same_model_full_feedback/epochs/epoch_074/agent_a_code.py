def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = [0, 0]
    best_score = -10**18

    # If no resources are visible, drift toward opponent to contest/deny progress.
    if not resources:
        resources = [(ox, oy)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        opp_sep = cheb(nx, ny, ox, oy)
        my_best = -10**18

        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Prefer getting closer than opponent; add a small preference for low my_d.
            val = (op_d - my_d) * 50 - my_d * 3
            if (rx, ry) == (nx, ny):
                val += 10**6
            # Slightly prioritize moves that keep us from being trapped far from resources.
            val += (8 - my_d) if my_d <= 8 else 0
            if val > my_best:
                my_best = val

        # Also prefer increasing separation from opponent when contest advantage is similar.
        score = my_best + opp_sep
        if score > best_score:
            best_score = score
            best_mv = [dx, dy]

    return [int(best_mv[0]), int(best_mv[1])]