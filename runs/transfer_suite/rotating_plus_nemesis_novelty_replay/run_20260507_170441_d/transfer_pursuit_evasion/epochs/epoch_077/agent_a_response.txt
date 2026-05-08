def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2): return max(abs(x1 - x2), abs(y1 - y2))
    def blocked_n(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if not free(nx, ny):
                    c += 1
        return c

    self_role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If pursuer: chase while preferring mobility (avoid getting boxed near obstacles/boundary).
    # If evader: run away while avoiding positions that are easy for a pursuer to trap.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        mob = 8 - blocked_n(nx, ny)  # higher is better
        # Boundary penalty to reduce "wall-sticking" for pursuer (keep controllable space).
        boundary = (1 if nx == 0 else 0) + (1 if nx == w - 1 else 0) + (1 if ny == 0 else 0) + (1 if ny == h - 1 else 0)

        if evader:
            # maximize distance; also prefer positions with fewer blocked neighbors (more escape options)
            # and mild preference for moving toward farthest corner to sustain survival.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_dist = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            score = (d, mob, corner_dist, -boundary)
        else:
            # minimize distance; prefer mobility and avoid edges (except when it helps cornering via distance)
            score = (-d, mob, -boundary)

        # Deterministic tie-breaker
        key = score + (dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]