def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; if tie, deny by making opponent slower.
        # Small deterministic tiebreaker by coordinates.
        key = (sd, -od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        # Move greedily toward target, but if opponent is closer, bias toward denying by
        # decreasing our distance relative to opponent's (approx 1-step effect).
        myd = dist(nx, ny, rx, ry)
        opd = dist(ox, oy, rx, ry)
        deny_score = myd - opd
        # Higher deny_score is better when we are farther; but we want smaller myd and
        # also smaller deny_score (we want to be closer than opponent).
        val = (myd, deny_score, abs(nx - rx) + abs(ny - ry), nx, ny, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]