def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or (role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obs(x, y):
        n = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    n += 1
        return n

    if is_pursuer:
        # Pursuer: minimize distance; also avoid getting boxed by obstacles.
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dist = cheb(nx, ny, ox, oy)
            val = dist * 100 + near_obs(nx, ny) * 3 + (abs(nx - ox) + abs(ny - oy)) * 0.05
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    else:
        # Evader: maximize distance from pursuer, but don't step into immediate danger near obstacles.
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dist = cheb(nx, ny, ox, oy)
            val = -dist * 100 - (abs(nx - ox) + abs(ny - oy)) * 0.1 + near_obs(nx, ny) * 5
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]