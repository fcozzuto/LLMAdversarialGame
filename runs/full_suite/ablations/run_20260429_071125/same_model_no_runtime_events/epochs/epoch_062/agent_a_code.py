def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_here = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Choose best contested resource based on who can reach it sooner
            best_adv = -10**18
            best_self_dist = 10**9
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                adv = od - sd  # positive means we are closer
                if adv > best_adv or (adv == best_adv and sd < best_self_dist):
                    best_adv = adv
                    best_self_dist = sd
            # Prefer higher advantage; also avoid letting opponent get much closer
            val = best_adv * 10 - best_self_dist
            # Small tie-breakers: keep distance from opponent and move toward resources corridor
            opp_dist = cheb(nx, ny, ox, oy)
            val += (opp_dist - opp_here) * 0.2
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # No visible resources: drift toward center while maximizing distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dc = cheb(nx, ny, cx, cy)
            dp = cheb(nx, ny, ox, oy)
            val = dp * 2 - dc
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]