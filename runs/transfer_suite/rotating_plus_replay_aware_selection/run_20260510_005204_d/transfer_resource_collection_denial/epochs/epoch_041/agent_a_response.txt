def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if (sx, sy) in obstacles:
        return [0, 0]

    # Pick a target resource that we are more likely to secure sooner than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer; otherwise prefer resources we can reach quickly
        # that also keep opponent from gaining an advantage.
        key = (myd - opd, myd, -(rx + ry), -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    if (sx, sy) == (tx, ty):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # For each candidate move, rank by minimizing our distance to target and maximizing opponent delay.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Score: primary reduce our distance; secondary increase opponent distance advantage (opponent farther).
        # Small deterministic bias breaks ties toward movement that progresses x then y.
        prog = -(abs(nx - tx) + abs(ny - ty))
        key = (myd2, -(opd2 - myd2), -prog, dx * 0 + 0)
        candidates.append((key, [dx, dy]))

    # If all moves blocked, stay.
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]