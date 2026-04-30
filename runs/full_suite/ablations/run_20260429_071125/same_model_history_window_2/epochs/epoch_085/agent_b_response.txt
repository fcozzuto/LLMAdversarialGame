def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx = (w - 1) * 0.5
    cy = (h - 1) * 0.5

    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        # Evaluate move by best achievable advantage over opponent across remaining resources.
        best_resource_val = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer (Chebyshev distance, diagonal moves allowed)
            # Tie-break: prefer nearer target when adv equal; slight center bias.
            near = -ds
            center = -abs(nx - cx) - abs(ny - cy)
            val = adv * 1000 + near * 10 + center
            if val > best_resource_val:
                best_resource_val = val

        # Also discourage moving away from where we already have strong advantage.
        current_best = -10**18
        for rx, ry in resources:
            ds0 = cheb(sx, sy, rx, ry)
            do0 = cheb(ox, oy, rx, ry)
            adv0 = do0 - ds0
            val0 = adv0 * 1000 - ds0 * 10 - abs(sx - cx) - abs(sy - cy)
            if val0 > current_best:
                current_best = val0

        # Prefer improvement; otherwise keep move stable.
        total = best_resource_val + (best_resource_val - current_best) * 0.25
        if total > best_val:
            best_val = total
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]