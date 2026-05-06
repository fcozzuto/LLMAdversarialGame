def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose best target: get closer faster than opponent (cheb distance, diagonal allowed)
    best_target = resources[0]
    best_val = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        val = myd - 0.75 * opd + 0.02 * (myd != 0) * cheb(tx, ty, 0, 0)
        if best_val is None or val < best_val:
            best_val = val
            best_target = (tx, ty)

    tx, ty = best_target

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    # Pick move that improves our distance to target while discouraging opponent progress
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        myd1 = cheb(sx, sy, tx, ty)
        # opponent best response not simulated; use current opponent distance to target as proxy
        opd = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; break ties by increasing opponent distance advantage
        improve = (myd1 - myd2)
        score = ( -improve, myd2, -(opd), abs((nx - tx) - (ny - ty)) )
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move