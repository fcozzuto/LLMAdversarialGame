def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    ox, oy = observation.get("opponent_position", (0, 0))
    tx = 3 if sx <= 3 else 4 if sx >= 4 else sx
    ty = 3 if sy <= 3 else 4 if sy >= 4 else sy

    if resources:
        best = None
        for dx, dy, nx, ny in legal:
            # Score candidate: prefer resources where we are closer than opponent, then closer overall.
            # Tie-break deterministically by coordinates.
            local = None
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Higher is better: advantage, slight preference for being closer.
                val = (do - ds, -(ds), -((rx+ry) % 2), -rx, -ry)
                if local is None or val > local[0]:
                    local = (val, ds, rx, ry)
            # If multiple resources, take the best local value
            cand = (local[0], dx, dy, nx, ny)
            if best is None or cand[0] > best[0]:
                best = cand
        return [int(best[1]), int(best[2])]

    best = None
    for dx, dy, nx, ny in legal:
        val = (-(cheb(nx, ny, tx, ty)), dx, dy, nx, ny)
        if best is None or val > best[0]:
            best = (val, dx, dy)
    return [int(best[1]), int(best[2])]