def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    rem = int(observation.get("remaining_resource_count", 0) or 0)

    if resources and rem > 0:
        best_t = None
        best_key = None
        for rx, ry in resources:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            key = (d1 - 0.6 * d2, d1, d2, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = int(round(cx)), int(round(cy))

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        center_pen = abs(nx - cx) + abs(ny - cy)
        # Lower is better: move towards target; prefer being ahead of opponent; slight center bias.
        val = our_d - (0.7 if rem > 0 else 0.2) * cheb(ox, oy, tx, ty) + 0.08 * center_pen + 0.01 * (dx * dx + dy * dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]