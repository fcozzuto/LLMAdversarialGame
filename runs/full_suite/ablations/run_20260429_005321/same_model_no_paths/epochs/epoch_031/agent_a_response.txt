def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                v = -(cheb(nx, ny, cx, cy))
                if v > bestv:
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        center_bias = -0.03 * (abs(nx - cx) + abs(ny - cy))
        # Choose the resource that maximizes advantage from this candidate position
        best_adv = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; penalize where opponent is closer.
            adv = (d_op - d_me) * 10.0
            # Extra reward for being very close, to reduce dithering.
            adv += 1.5 / (1 + d_me)
            # If opponent is already closer, discourage strongly.
            if d_op < d_me:
                adv -= 8.0
            # Small tie-break by resource ordering deterministically
            adv -= 0.001 * (rx * 8 + ry)
            if adv > best_adv:
                best_adv = adv

        # If we step onto a resource, ensure it wins
        on_res = any((nx == rx and ny == ry) for rx, ry in resources)
        val = best_adv + center_bias + (500.0 if on_res else 0.0)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]