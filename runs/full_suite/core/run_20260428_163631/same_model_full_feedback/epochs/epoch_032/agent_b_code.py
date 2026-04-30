def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    resources_sorted = sorted(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), cheb(ox, oy, t[0], t[1]), t[0], t[1]))

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_score = -10**9
        for tx, ty in resources_sorted:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)

            # prefer targets we can reach no slower than opponent; otherwise reduce their advantage
            # also slightly prefer moving closer overall
            win_term = 20 if d_self <= d_opp else 0
            score = win_term + (d_opp - d_self) * 3 - d_self * 0.2

            # small obstacle-aware bias by discouraging stepping into cells that are adjacent to many obstacles
            adj = 0
            for ax, ay in dirs:
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj += 1
            score -= adj * 0.15

            if score > best_score:
                best_score = score
        candidates.append((best_score, nx, ny, dx, dy))

    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
    return [candidates[0][3], candidates[0][4]]