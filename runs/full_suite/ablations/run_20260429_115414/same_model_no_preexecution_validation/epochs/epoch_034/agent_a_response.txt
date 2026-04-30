def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_t = resources[0]
        best_score = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer denying opponent: reward do-ds and being closer to resource.
            score = (do - ds) * 10 - ds
            if score > best_score or (score == best_score and (rx, ry) < best_t):
                best_score = score
                best_t = (rx, ry)
        rx, ry = best_t
        best_move = (0, 0)
        best_val = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            nds = cheb(nx, ny, rx, ry)
            ndo = cheb(ox, oy, rx, ry)  # opponent stays; our move affects only nds
            # Also slightly prefer increasing distance from opponent to avoid collision/denial.
            sep = cheb(nx, ny, ox, oy)
            val = nds * 12 - ndo * 1 - sep * 0.5
            if val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No visible resources: move to center while keeping away from opponent.
        tx, ty = w // 2, h // 2
        best_move = (0, 0)
        best_val = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            dcenter = cheb(nx, ny, tx, ty)
            sep = cheb(nx, ny, ox, oy)
            val = dcenter * 2 - sep
            if val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]