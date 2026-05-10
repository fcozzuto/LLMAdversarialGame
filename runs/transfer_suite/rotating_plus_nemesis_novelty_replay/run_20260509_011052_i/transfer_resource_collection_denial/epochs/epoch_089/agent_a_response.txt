def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
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

    opp_center_bias = (ox - (w - 1) / 2.0) * 0.01 + (oy - (h - 1) / 2.0) * 0.01
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Strongly prefer resources we can reach earlier; then closer ones.
        margin = od - sd
        # If tied, bias away from opponent region to reduce immediate contest.
        opp_dist = cheb(ox, oy, rx, ry)
        side_bias = -opp_dist * 0.001 - (rx - (w - 1) / 2.0) * 0.0001 + (ry - (h - 1) / 2.0) * 0.0001
        key = (margin, -sd, side_bias - opp_center_bias)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose the next step that minimizes Chebyshev distance to target, avoiding obstacles/opponent.
    best_step = (0, 0)
    best_d = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) == (ox, oy):
                continue
            d = cheb(nx, ny, tx, ty)
            # Small tie-break: prefer moves that increase distance from opponent when not making progress.
            opp_d = cheb(nx, ny, ox, oy)
            key = (d, -opp_d)
            if best_d is None or key < best_d:
                best_d = key
                best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]