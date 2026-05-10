def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = (observation.get("self_role", "") or "").lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def obst_min_dist(nx, ny):
        best = 10**9
        for x, y in obstacles:
            d = abs(nx - x) + abs(ny - y)
            if d < best:
                best = d
        return best if best != 10**9 else 10**6

    def score_move(nx, ny):
        d = (abs(nx - ox) + abs(ny - oy))
        md = obst_min_dist(nx, ny)
        edge_pen = (nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)
        if pursuer:
            # Lower distance to opponent, strong penalty near obstacles; slight tie-breaker toward center
            s = -d * 10.0
            if md <= 0: s -= 1e6
            elif md == 1: s -= 30.0
            elif md == 2: s -= 8.0
            else: s -= md * 0.3
            s -= edge_pen * 0.2
            return s
        else:
            # Evade: maximize distance; bias toward a corner that changes with turn parity
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            ti = int(observation.get("turn_index", 0) or 0)
            idx = (ti + (sx + sy) * 3) % 4
            target = corners[idx]
            tc = abs(nx - target[0]) + abs(ny - target[1])
            # Prefer far from opponent, but also avoid getting boxed by obstacles
            s = d * 10.0 + tc * 0.6
            if md == 0: s -= 1e6
            elif md == 1: s -= 35.0
            elif md == 2: s -= 10.0
            else: s -= md * 0.15
            # Avoid hugging edges too much unless it helps the target corner
            s -= edge_pen * 0.35
            return s

    best = None
    best_s = -10**18
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        s = score_move(nx, ny)
        # deterministic tie-break: prefer move that changes position, then lexicographic dx,dy
        if best is None or s > best_s or (s == best_s and (nx != sx or ny != sy) and (dx < best[0] or (dx == best[0] and dy < best[1]))):
            best_s = s
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]