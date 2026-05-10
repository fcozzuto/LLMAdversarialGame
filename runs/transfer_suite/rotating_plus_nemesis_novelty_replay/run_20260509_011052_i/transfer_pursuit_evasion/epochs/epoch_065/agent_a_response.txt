def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            if inb(x + dx, y + dy):
                m += 1
        return m

    best = None
    if pursuer:
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            val = -d * 10 + mobility(nx, ny)
            if nx == ox and ny == oy:
                val = 10**12
            # Tie-break deterministically: prefer moves with smaller (nx,ny) lexicographically
            if best is None or val > best_val or (val == best_val and (nx, ny) < best):
                best_val = val
                best = (nx, ny, dx, dy)
        return [best[2], best[3]] if best else [0, 0]
    else:
        best_val = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            val = d * 10 - mobility(nx, ny)
            if nx == ox and ny == oy:
                val = -10**12
            if best is None or val < best_val or (val == best_val and (nx, ny) < best):
                best_val = val
                best = (nx, ny, dx, dy)
        return [best[2], best[3]] if best else [0, 0]