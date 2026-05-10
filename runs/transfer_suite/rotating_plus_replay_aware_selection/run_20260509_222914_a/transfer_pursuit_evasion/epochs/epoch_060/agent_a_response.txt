def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score(nx, ny):
        # obstacle proximity penalty
        prox = 0
        if (nx, ny) in obstacles:
            return -10**9 if is_pursuer else 10**9
        for ox2, oy2 in obstacles:
            m = abs(nx - ox2) + abs(ny - oy2)
            if m == 0:
                prox += 5
            elif m == 1:
                prox += 2
            elif m == 2:
                prox += 1
        d = dist(nx, ny, ox, oy)
        # pursuer: smaller d better; evader: larger d better
        base = -d if is_pursuer else d
        # discourage staying if multiple equal options (deterministic tie-breaker via penalty)
        stay_pen = 1 if (nx == sx and ny == sy) else 0
        return base - (3 * prox + 0.1 * stay_pen)

    # evader extra: bias toward farthest corner from opponent for stronger evasion
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if not is_pursuer:
        far_corner = max(corners, key=lambda c: dist(c[0], c[1], ox, oy))
    else:
        far_corner = None

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            nx2, ny2 = sx, sy
            nx, ny = nx2, ny2
        s = score(nx, ny)
        if not is_pursuer and far_corner is not None:
            s += 0.15 * dist(nx, ny, far_corner[0], far_corner[1])
        if best is None or s > best:
            best = s
            best_move = [dx, dy]
    return best_move