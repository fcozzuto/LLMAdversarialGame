def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    opp_close = king(sx, sy, ox, oy) <= 2

    best_move = (0, 0, -10**18)
    for dx, dy, nx, ny in valid:
        # Evasion/spacing from safe_collector when too close
        spacing = king(nx, ny, ox, oy)
        if opp_close and spacing <= 1:
            val = -1000 + spacing
        else:
            # Pick the most "secure" resource from the candidate position:
            # maximize (opp_dist - self_dist), lightly favor closeness to avoid stalemates.
            val = -10**18
            for rx, ry in resources:
                sd = king(nx, ny, rx, ry)
                od = king(ox, oy, rx, ry)
                # Prefer resources we can reach at least as fast, otherwise still try to steal with margin.
                margin = od - sd
                secure = margin * 8 - sd
                # Mild center preference to keep pressure in middle without large search.
                cx = (w - 1) / 2.0
                cy = (h - 1) / 2.0
                center = -abs(rx - cx) - abs(ry - cy)
                cur = secure + 0.15 * center
                if cur > val:
                    val = cur
            if val == -10**18:
                # No resources: drift toward center while avoiding opponent
                cx = (w - 1) / 2.0
                cy = (h - 1) / 2.0
                val = -(abs(nx - cx) + abs(ny - cy)) + 0.5 * spacing
        if val > best_move[2] or (val == best_move[2] and (dx, dy) < (best_move[0], best_move[1])):
            best_move = (dx, dy, val)

    return [best_move[0], best_move[1]]