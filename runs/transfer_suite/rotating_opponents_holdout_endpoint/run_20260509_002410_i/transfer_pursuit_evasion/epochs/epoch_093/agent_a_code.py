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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def obs_near(x, y):
        n = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    n += 1
        return n

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        nnear = obs_near(nx, ny)
        # Also discourage stepping into opponent line-ish when pursuing (roughly)
        align = -cheb(nx, ny, ox, ny) - cheb(nx, ny, nx, oy)

        if is_pursuer:
            # minimize distance; break ties by safer / stronger alignment
            key = (d, nnear, -align, abs(dx) + abs(dy))
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        else:
            # maximize distance; break ties by safer
            key = (-d, nnear, -align, abs(dx) + abs(dy))
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]

    if best is None:
        # fallback: stay put
        return [0, 0]
    return best