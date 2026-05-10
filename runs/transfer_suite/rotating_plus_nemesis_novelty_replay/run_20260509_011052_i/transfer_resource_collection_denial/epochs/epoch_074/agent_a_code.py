def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can beat; then shortest to us; then farthest from opponent; then deterministic tie-break.
        key = (od - sd, -sd, od, -(rx + ry), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    ddx = tx - sx
    if ddx > 0: step_x = 1
    elif ddx < 0: step_x = -1
    else: step_x = 0
    ddy = ty - sy
    if ddy > 0: step_y = 1
    elif ddy < 0: step_y = -1
    else: step_y = 0

    candidates = []
    candidates.append((step_x, step_y))  # diagonal/straight toward target
    # If diagonal not possible, try single-axis moves deterministically; if axis is already aligned, it will duplicate.
    if step_x != 0: candidates.append((step_x, 0))
    if step_y != 0: candidates.append((0, step_y))
    candidates.append((0, 0))

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            return [int(dx), int(dy)]
    return [0, 0]