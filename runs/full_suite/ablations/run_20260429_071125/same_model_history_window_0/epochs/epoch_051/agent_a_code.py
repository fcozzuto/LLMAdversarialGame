def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def sgn(v):
        return (v > 0) - (v < 0)

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, drift toward center while avoiding obstacles
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Choose resource where we are relatively closer than opponent
        best = None
        for rx, ry in resources:
            myd = cheb((sx, sy), (rx, ry))
            opd = cheb((ox, oy), (rx, ry))
            key = (myd - opd, myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    cx = tx - sx
    cy = ty - sy

    # Candidate moves in deterministic order (prefer toward target with diagonals)
    pref = [
        (sgn(cx), sgn(cy)),
        (sgn(cx), 0),
        (0, sgn(cy)),
        (sgn(cx), -sgn(cy)),
        (-sgn(cx), sgn(cy)),
        (-sgn(cx), 0),
        (0, -sgn(cy)),
        (-sgn(cx), -sgn(cy)),
        (0, 0),
    ]
    seen = set()
    moves = []
    for dx, dy in pref:
        if (dx, dy) not in seen:
            seen.add((dx, dy))
            moves.append((dx, dy))

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles and (dx, dy) != (0, 0):
            continue
        myd = cheb((nx, ny), (tx, ty))
        # Relative advantage estimate vs opponent staying put this turn
        opd = cheb((ox, oy), (tx, ty))
        val = (myd - opd, myd, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]