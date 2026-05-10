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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_target = None

    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; then closer; then upper-left tie-break.
        score = (opd - myd) * 10000 - myd * 10
        if score > 0 or score == 0:
            pass
        tie = -rx * 1 - ry * 0  # deterministic
        total = score + tie
        if best_score is None or total > best_score:
            best_score = total
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = [0, 0]
    best_val = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        # Value: reduce distance to target, avoid stepping away if opponent threatening same target.
        myd2 = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        myd0 = cheb(sx, sy, tx, ty)
        # Small bias to keep progress when close.
        val = (opd - myd2) * 10000 - myd2 * 10 + (myd0 - myd2)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]