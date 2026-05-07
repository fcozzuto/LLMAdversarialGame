def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

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

    # Prefer resources we can reach earlier; if none, prefer those where we are closest among ties.
    best = None
    best_key = None
    tr = int(observation.get("turns_remaining") or 0)
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Later resources lose value; scale lightly but deterministically.
        urgency = (tr - sd)
        key = (-(od - sd), sd, -urgency, rx, ry)  # maximize: smallest (od-sd), then smallest sd
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    if sx == rx and sy == ry:
        return [0, 0]

    # Move one step toward target; if diagonal blocked by obstacle, fall back to axis move.
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)
    nx, ny = sx + dx, sy + dy
    if (0 <= nx < w and 0 <= ny < h) and (nx, ny) not in obstacles:
        return [dx, dy]

    # Try axis directions deterministically: x then y.
    nx = sx + dx
    if 0 <= nx < w and (nx, sy) not in obstacles:
        return [dx, 0]
    ny = sy + dy
    if 0 <= ny < h and (sx, ny) not in obstacles:
        return [0, dy]
    return [0, 0]