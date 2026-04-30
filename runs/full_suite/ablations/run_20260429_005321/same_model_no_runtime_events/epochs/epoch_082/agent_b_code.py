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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            # Move to improve closeness to nearest resource, and contest if opponent is close.
            d_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            # If opponent is closer to the same resource, prefer moves that reduce that gap.
            gap = d_self - d_opp
        else:
            d_self = 0
            gap = 0

        # Discourage getting too close to opponent (reduce collision/steal risk).
        d_adv = cheb(nx, ny, ox, oy)
        opp_pressure = 1.0 / (1 + d_adv)

        score = 10.0 * (-d_self) - 6.0 * gap - 2.5 * opp_pressure
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move