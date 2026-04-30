def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obst = set((x, y) for x, y in obstacles)
    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        dx = -dx if dx < 0 else dx
        dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy  # Chebyshev

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_val = None
    for rx, ry in resources:
        if not in_bounds(rx, ry) or (rx, ry) in obst:
            continue
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        val = myd - 0.6 * opd  # prefer resources opponent is farther from
        if best is None or val < best_val:
            best = (rx, ry)
            best_val = val

    tx, ty = best
    dxi = 0
    dyi = 0
    if tx > sx:
        dxi = 1
    elif tx < sx:
        dxi = -1
    if ty > sy:
        dyi = 1
    elif ty < sy:
        dyi = -1

    candidates = []
    primary = (dxi, dyi)
    candidates.append(primary)
    for dxx in (-1, 0, 1):
        for dyy in (-1, 0, 1):
            if (dxx, dyy) == primary:
                continue
            if (dxx, dyy) == (0, 0):
                continue
            candidates.append((dxx, dyy))
    candidates.append((0, 0))

    best_step = (0, 0)
    best_score = None
    for dxx, dyy in candidates:
        nx, ny = sx + dxx, sy + dyy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue
        nd = dist((nx, ny), (tx, ty))
        opp_nd = dist((ox, oy), (tx, ty))
        step_score = nd + 0.05 * abs(dxx) + 0.05 * abs(dyy) - 0.0 * opp_nd
        if best_score is None or step_score < best_score:
            best_score = step_score
            best_step = (dxx, dyy)

    return [int(best_step[0]), int(best_step[1])]