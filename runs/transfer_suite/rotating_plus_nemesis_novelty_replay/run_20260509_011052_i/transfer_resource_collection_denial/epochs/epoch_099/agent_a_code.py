def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def sgn(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # First prefer resources we can reach no later than opponent; then pick smallest sd,
        # but if losing, pick where opponent is "least ahead" (smallest od - sd).
        if sd <= od:
            key = (0, sd, -od, rx, ry)
        else:
            key = (1, od - sd, od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx, dy = sgn(tx - sx), sgn(ty - sy)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]
    # Try axis-first detours deterministically.
    if dx != 0 and valid(sx + dx, sy):
        return [dx, 0]
    if dy != 0 and valid(sx, sy + dy):
        return [0, dy]
    # Try diagonal without one component if still blocked.
    if valid(sx + dx, sy) is False and valid(sx, sy + dy) is False:
        return [0, 0]
    return [0, 0]