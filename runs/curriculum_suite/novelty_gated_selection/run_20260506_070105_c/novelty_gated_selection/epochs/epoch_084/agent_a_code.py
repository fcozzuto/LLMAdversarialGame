def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # No resources: drift to center while keeping distance from opponent.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            dcent = man(nx, ny, cx, cy)
            opp = man(nx, ny, ox, oy)
            key = (dcent, -opp, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Race to resources where we can arrive first (margin = opp_dist - my_dist).
    # Also discourage stepping into positions where opponent is significantly closer.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        best_margin = -10**9
        best_my_dist = 10**9
        best_opp_dist = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            margin = opd - myd
            if margin > best_margin or (margin == best_margin and myd < best_my_dist):
                best_margin = margin
                best_my_dist = myd
                best_opp_dist = opd

        # If we can realistically beat opponent (positive margin), prioritize it.
        # Otherwise, still prefer getting closer to a resource and not allowing immediate capture.
        opp_now = man(nx, ny, ox, oy)
        # penalize being near opponent when our best margin is not positive
        penalty = 0
        if best_margin <= 0:
            penalty = max(0, 6 - opp_now) * 2 + best_opp_dist
        key = (-best_margin, best_my_dist + penalty, -opp_now, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]