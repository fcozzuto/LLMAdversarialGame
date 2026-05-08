def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y):
        dx = x - ox
        if dx < 0: dx = -dx
        dy = y - oy
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if inb(x + ax, y + ay):
                    c += 1
        return c

    self_role = (observation.get("self_role") or "")
    pursuer = ("pursuer" in self_role.lower()) or (self_role.lower() == "pursuer")

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_mv = (0, 0)

    # Tie-breaker prefers moves that keep options open and avoid tight corners near obstacles.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny)
        m = mobility(nx, ny)
        center_bias = -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)
        # obstacle tightness: count blocked neighbors
        tight = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if not inb(tx, ty):
                    tight += 1

        if pursuer:
            sc = -d + 0.08 * m - 0.03 * tight + 0.01 * center_bias
        else:
            sc = d + 0.08 * m - 0.03 * tight + 0.01 * (-center_bias)

        if best is None or sc > best:
            best = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]