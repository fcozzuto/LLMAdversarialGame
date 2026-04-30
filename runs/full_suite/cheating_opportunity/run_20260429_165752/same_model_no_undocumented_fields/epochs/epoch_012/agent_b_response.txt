def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs.add((int(o[0]), int(o[1])))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    valids = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                valids.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if (x, y) in obs:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    if not valids:
        # Deterministic fallback: drift toward center while avoiding obstacles.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny, tx, ty)
            if (d, cheb(nx, ny, ox, oy), dx, dy) < (best[0], best[1], best[2], best[3]):
                best = (d, cheb(nx, ny, ox, oy), dx, dy)
        return [best[2], best[3]]

    # Pick resource where we have maximal reach advantage over opponent.
    best_res = None
    best_key = (-10**9, 10**9, 10**9)  # (opp-self, self_dist, center_dist)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for rx, ry in valids:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - sd
        cd = abs(rx - cx) + abs(ry - cy)
        key = (advantage, sd, cd)
        if key > best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    # Step: minimize our distance to target; if tied, break by reducing opponent distance and then by move order.
    best_move = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d1 = cheb(nx, ny, rx, ry)
        d2 = cheb(nx, ny, ox, oy)
        # Prefer moves that also shrink opponent-to-target gap (strategic denial).
        opp_d = cheb(ox, oy, rx, ry)
        after_gap = opp_d - d1
        key = (d1, -after_gap, d2, dx, dy)
        if key < (best_move[0], best_move[1], best_move[2], best_move[3], best_move[4]):
            best_move = (d1, -after_gap, d2, dx, dy)

    return [int(best_move[3]), int(best_move[4])]