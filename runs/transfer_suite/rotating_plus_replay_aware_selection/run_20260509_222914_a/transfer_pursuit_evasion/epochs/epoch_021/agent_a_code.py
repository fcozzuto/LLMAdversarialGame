def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role) or ("pursuer" in self_role)
    moves = [(0, 0), (1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def free(nx, ny): return inb(nx, ny) and (nx, ny) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Immediate capture check (if allowed by engine, still safe)
    if pursuer:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) == (ox, oy) and free(nx, ny):
                return [int(dx), int(dy)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    wall_bias = lambda nx, ny: min(nx, w - 1 - nx, ny, h - 1 - ny)

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)

        if pursuer:
            # Prefer smaller distance; then move to positions with more mobility (avoid dead-ends)
            mobility = 0
            for mdx, mdy in moves:
                tx, ty = nx + mdx, ny + mdy
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    mobility += 1
            val = (-d * 100.0) + mobility + (1.0 if nx in (0, w - 1) or ny in (0, h - 1) else 0.0)
        else:
            # Evader: maximize distance; avoid walls; also prefer center vs being pinned by obstacles
            mobility = 0
            for mdx, mdy in moves:
                tx, ty = nx + mdx, ny + mdy
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    mobility += 1
            dist_center = abs(nx - cx) + abs(ny - cy)
            val = (d * 100.0) + (wall_bias(nx, ny) * 3.0) + (mobility * 0.5) - (dist_center * 0.8)

        if best is None or (val > best_val) or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]