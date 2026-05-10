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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    # Prefer staying away from obstacles; stronger if closer to an obstacle.
    def obst_pen(x, y):
        p = 0
        for (ex, ey) in obstacles:
            d = abs(x - ex) + abs(y - ey)
            if d == 0:
                return 10**9
            if d <= 2:
                p += (3 - d) * 40
        return p

    # For evasion, favor the corner farthest from pursuer (deterministic "escape target").
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best = None
    best_score = None

    # Deterministic tie-breaker preference order: moves are scanned in dirs order.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        p = obst_pen(nx, ny)

        if is_evader:
            # Maximize distance to pursuer, then push toward escape corner.
            d_corner = dist2(nx, ny, corner[0], corner[1])
            score = (d_opp * 10) + (d_corner) - p
        else:
            # Minimize distance to evader; discourage obstacles.
            score = (-d_opp * 10) - p
            # Small bias: approach via both axes more (Chebyshev-like).
            score -= max(abs(nx - ox), abs(ny - oy)) * 0.5

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best