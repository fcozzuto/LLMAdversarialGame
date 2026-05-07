def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

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

    # If already on a resource, take it
    if (sx, sy) in set(tuple(r) for r in resources):
        return [0, 0]

    # Choose target: prefer resources where we are strictly closer than opponent; then maximize closeness advantage
    best = None
    best_key = None
    for rx, ry in resources:
        my = cheb(sx, sy, rx, ry)
        op = cheb(ox, oy, rx, ry)
        advantage = op - my  # positive if we are closer
        tie = (advantage, -my, -op, rx, ry)
        if advantage > 0:
            if best_key is None or tie > best_key:
                best_key = tie
                best = (rx, ry)
        else:
            if best is None:
                best = (rx, ry)
                best_key = (advantage, -my, -op, rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_dist = None
    best_block = False

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        if best_dist is None or d < best_dist or (d == best_dist and (dx, dy) < best_move):
            best_dist = d
            best_move = (dx, dy)

    if best_dist is not None:
        return [best_move[0], best_move[1]]

    # Fallback: move to any in-bounds non-obstacle cell minimizing distance to opponent target line (simple center-out)
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((cheb(nx, ny, ox, oy), dx, dy))
    if cand:
        cand.sort()
        return [cand[0][1], cand[0][2]]

    return [0, 0]