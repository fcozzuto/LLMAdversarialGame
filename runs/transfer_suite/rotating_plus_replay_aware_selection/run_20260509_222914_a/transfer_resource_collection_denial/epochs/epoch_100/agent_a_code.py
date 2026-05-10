def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_target(rx, ry):
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can arrive at significantly earlier.
        # Small negative bias to reduce dithering among equidistant targets.
        return (od - sd, -sd, rx, ry)

    target = None
    best = None
    for rx, ry in resources:
        sc = score_target(rx, ry)
        if best is None or sc > best:
            best = sc
            target = (rx, ry)
    tx, ty = target

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        # Greedy step toward target, but also consider whether we are blocking opponent resources.
        sd_next = cheb(nx, ny, tx, ty)
        od_to_target = cheb(ox, oy, tx, ty)
        # Value: reduce our distance; if we're ahead, prioritize further; if behind, try to catch up.
        ahead = od_to_target - sd_next
        # Tie-break: keep closer to center-ish to avoid edge traps deterministically.
        center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2)
        val = (ahead, -sd_next, center_bias)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return best_move