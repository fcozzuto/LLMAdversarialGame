def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def obst_adj_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        # Penalize standing too close to obstacles (avoid trapping near blocks)
        p = 0
        for ex, ey in obstacles:
            d = abs(x - ex) + abs(y - ey)
            if d == 1:
                p += 25
            elif d == 2:
                p += 8
        return p

    def corner_bias(x, y):
        # Encourage evader to cling to corners; slight for pursuer to avoid them
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        return max(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = dist2(nx, ny, ox, oy)
        pen = obst_adj_pen(nx, ny)
        # Extra: keep movement from becoming "stuck" by preferring corner for evader and center-ish for pursuer
        if is_evader:
            score = d * 1.0 - pen * 1.0 + corner_bias(nx, ny) * 0.05
        else:
            score = -d * 1.0 - pen * 1.0 - corner_bias(nx, ny) * 0.02
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    # Fallback (all moves invalid): stay put
    return best if best is not None else [0, 0]