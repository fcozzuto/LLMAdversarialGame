def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if resources:
        centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Heuristic: prefer resources I can reach earlier; break ties by being closer.
            val = 0.0
            # Small bias away from being directly between opponent and center.
            val += 0.02 * ((nx - ox) * (centerx - ox) + (ny - oy) * (centery - oy))
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                d = opd - myd  # positive if I'm closer
                # Encourage winning races; discourage long myd.
                val += 6.0 * (d if d > 0 else -0.15 * (-d)) - 0.55 * myd
            # Prefer fewer steps overall by also considering opponent distance to my chosen cell.
            val -= 0.08 * cheb(ox, oy, nx, ny)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # No resources: move to center while avoiding staying adjacent to opponent.
        targetx, targety = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            my_to_center = cheb(nx, ny, targetx, targety)
            opp_to_next = cheb(ox, oy, nx, ny)
            val = -1.2 * my_to_center + 0.35 * opp_to_next
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]