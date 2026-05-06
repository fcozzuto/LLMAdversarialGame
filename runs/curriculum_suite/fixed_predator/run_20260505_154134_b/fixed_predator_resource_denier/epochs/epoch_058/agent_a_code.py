def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx, cy = w // 2, h // 2

    if not resources:
        best = None
        bestv = -10**9
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = cheb(nx, ny, cx, cy) * -1
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    best = (0, 0)
    bestv = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate by the best "breakthrough" resource we can contest next.
        # Higher: opponent farther than us for some resource.
        # Secondary: prefer being closer to center and closer to that resource.
        local_best = -10**18
        local_best_selfd = 10**9
        local_best_cent = 10**9

        centd = cheb(nx, ny, cx, cy)
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - sd  # positive means we are closer than opponent for this resource
            # Encourage selecting a resource we can realistically reach soon.
            v = gap * 100 - sd
            if v > local_best or (v == local_best and (sd < local_best_selfd or (sd == local_best_selfd and centd < local_best_cent))):
                local_best = v
                local_best_selfd = sd
                local_best_cent = centd

        # Small tie-break to reduce oscillation toward center.
        final_v = local_best - centd * 0.5
        if final_v > bestv:
            bestv = final_v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]