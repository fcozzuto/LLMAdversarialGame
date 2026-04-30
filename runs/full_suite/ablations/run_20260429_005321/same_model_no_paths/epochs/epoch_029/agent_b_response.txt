def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -cheb(nx, ny, cx, cy) + 0.03 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        opp_d = cheb(nx, ny, ox, oy)
        # Score: pick the resource that we can reach sooner than opponent (opp_dist - our_dist).
        # Also encourage direct approach and reduce useless closeness to opponent.
        best_contested = -10**9
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            their_d = cheb(ox, oy, rx, ry)
            contested = their_d - our_d
            # Tie-break toward nearer-to-resource and away from opponent.
            val = contested - 0.02 * our_d - 0.01 * max(0, our_d - their_d)
            if val > best_contested:
                best_contested = val
        v = best_contested + 0.005 * (cheb(nx, ny, cx, cy) * -1) - 0.015 * opp_d
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]