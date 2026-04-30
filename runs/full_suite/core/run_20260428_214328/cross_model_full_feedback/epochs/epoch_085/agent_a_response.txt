def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # "New policy": evaluate move by next-position advantage over the best contested resource,
    # plus a small "intercept" term to reduce opponent's ability to reach that resource first.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # If we can capture immediately, prioritize.
        immediate = 1 if (nx, ny) in seen else 0

        d_me = cheb(nx, ny, ox, oy)  # proxy for contest pressure
        best_res = 0
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # Strongly favor resources where opponent is farther; also deny those where they are closer.
            val = (d2 - d1) * 40 - d1
            # Intercept: if we are close enough to arrive soon, add slight bonus.
            if d1 <= 2:
                val += 15
            # If we are moving away from our current closest contest, penalize.
            val -= (d_me // 3)
            if val > best_res:
                best_res = val

        # Center bias to avoid corner-sink when resources are sparse.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = - (abs(nx - cx) + abs(ny - cy))

        score = immediate * 10**6 + best_res + center
        if score > best_val:
            best_val = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]