def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Select target deterministically: maximize "advantage" with a small closeness bonus to break ties.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            closeness = -(ds + 0.02 * (rx + ry))  # slight deterministic tie-break
            key = (adv, closeness, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources visible: keep position (deterministic).
        return [0, 0]

    # Move one step that improves toward target while avoiding obstacles; also consider opponent pressure.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ds2 = cheb(nx, ny, tx, ty)

        # Opponent "pressure": prefer states where opponent is not significantly closer to the target.
        do = cheb(ox, oy, tx, ty)
        pressure = do - ds2  # want non-negative or larger

        # Small penalties to prevent oscillation: prefer lower ds2, then prefer moving (not necessarily).
        key_score = (pressure, -ds2, -(dx == 0 and dy == 0), -abs(nx - ox) - abs(ny - oy))
        if best_score is None or key_score > best_score:
            best_score = key_score
            best_move = [dx, dy]

    return best_move