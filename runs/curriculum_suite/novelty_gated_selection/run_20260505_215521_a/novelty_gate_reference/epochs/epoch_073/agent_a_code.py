def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose resource that we can reach earlier than opponent, with tie-breakers.
    best = None
    best_val = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        ahead = opd - myd  # positive => we are closer
        # Favor resources that are "off the opponent's likely lane" (y differs) and not too close to us.
        val = ahead * 1000 + (abs(ry - oy) * 10) - (myd * 2) - (abs(rx - sx) * 1)
        # Deterministic tie-break by coordinates.
        if best is None or val > best_val or (val == best_val and (rx, ry) < best):
            best_val = val
            best = (rx, ry)

    tx, ty = best

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    # Primary move: toward target diagonally if possible.
    nx, ny = sx + dx, sy + dy
    if (dx != 0 or dy != 0) and valid(nx, ny):
        return [dx, dy]

    # Fallback: try axis moves in deterministic priority toward reducing Chebyshev distance.
    candidates = []
    if dx != 0:
        candidates.append((dx, 0))
    if dy != 0:
        candidates.append((0, dy))
    # If both blocked or zero, consider staying.
    candidates.append((0, 0))

    # Ensure deterministic order and avoid obstacles.
    # If diagonal blocked, prefer the move that decreases cheb most.
    scored = []
    for ddx, ddy in candidates:
        cx, cy = sx + ddx, sy + ddy
        if not valid(cx, cy):
            continue
        scored.append(((cheb(cx, cy, tx, ty), ddx, ddy), [ddx, ddy]))
    if not scored:
        return [0, 0]
    scored.sort(key=lambda z: (z[0][0], z[0][1], z[0][2]))
    return scored[0][1]