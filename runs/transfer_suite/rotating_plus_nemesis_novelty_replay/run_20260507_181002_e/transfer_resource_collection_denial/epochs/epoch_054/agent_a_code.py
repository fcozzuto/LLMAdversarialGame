def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = get_xy(observation.get("self_position", None), (0, 0))
    ox, oy = get_xy(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = get_xy(o, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = get_xy(r, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Deterministic ordering to break ties consistently
    moves.sort(key=lambda m: (m[0], m[1]))

    def best_for(posx, posy):
        best = (-10**9, 10**9)  # (score, self_dist)
        for rx, ry in resources:
            self_d = abs(rx - posx) + abs(ry - posy)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we can reach sooner than opponent; also prefer closer overall.
            score = (opp_d - self_d) * 100 - self_d
            # Slight preference for centralization to reduce corner traps
            center = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
            score -= int(center)
            if score > best[0] or (score == best[0] and self_d < best[1]):
                best = (score, self_d)
        return best[0], best[1]

    best_move = None
    best_val = (-10**18, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        val = best_for(nx, ny)
        if val[0] > best_val[0] or (val[0] == best_val[0] and val[1] < best_val[1]):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]