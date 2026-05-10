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
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    moves = [(0, 0), (1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def free(nx, ny): return inb(nx, ny) and (nx, ny) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Evader/ pursuer immediate contact
    if pursuer:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) == (ox, oy) and free(nx, ny):
                return [int(dx), int(dy)]

    candidates = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # Use deterministic tie-break: smaller index via dx,dy ordering already in moves
        if pursuer:
            # Prefer smaller distance, but also avoid stepping away too much due to obstacles
            score = (d, abs(nx - x) + abs(ny - y))
            candidates.append((score, dx, dy))
        else:
            # Prefer larger distance; also bias toward corners deterministically
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            # Choose corner farthest from opponent (static) for bias
            best_corner = 0
            best_cd = -1
            for cxi, cyi in corners:
                cd = cheb(cxi, cyi, ox, oy)
                if cd > best_cd:
                    best_cd = cd
                    best_corner = (cxi, cyi)
            cx, cy = best_corner
            corner_bias = cheb(nx, ny, cx, cy)  # want smaller distance to corner
            # Primary maximize d, secondary minimize corner_bias, then tie by move distance
            score = (-d, corner_bias, abs(nx - x) + abs(ny - y))
            candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    # Deterministic selection: minimal score tuple
    candidates.sort(key=lambda t: (t[0][0], t[0][1], t[0][2], t[1], t[2]) if len(t[0]) > 2 else (t[0][0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]