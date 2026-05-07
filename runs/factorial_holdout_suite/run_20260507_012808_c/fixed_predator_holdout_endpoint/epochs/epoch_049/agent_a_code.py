def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inb(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    # Choose move that advances toward a promising resource while avoiding moves that let the opponent "shadow" too closely.
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        # Find best resource for this move under relative-advantage metric.
        best_res = None
        best_res_val = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Want to be significantly closer than opponent.
            rel = (do - ds)
            v = rel * 1000 - ds  # strongly prefer becoming the nearer collector
            if v > best_res_val:
                best_res_val = v
                best_res = (rx, ry)

        rx, ry = best_res
        ds = cheb(nx, ny, rx, ry)
        do_after = cheb(ox, oy, rx, ry)

        # Denial/shadow penalty: if we move into a cell from which opponent is very close to our target area, back off.
        opp_near = cheb(ox, oy, nx, ny)
        shadow_pen = 0
        if opp_near <= 1:
            shadow_pen = 400

        # Also avoid stepping onto or adjacent to all resources (can get trapped by denial).
        adj_resource = 0
        for r in resources:
            if cheb(nx, ny, r[0], r[1]) <= 1:
                adj_resource += 1
        adj_pen = adj_resource * 20

        # Small preference to center-ish to reduce cornering risk.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pref = - (abs(nx - cx) + abs(ny - cy))

        # Final score: maximize.
        val = (best_res_val // 1) + center_pref - shadow_pen - adj_pen - (ds * 2) + (do_after * 1)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]