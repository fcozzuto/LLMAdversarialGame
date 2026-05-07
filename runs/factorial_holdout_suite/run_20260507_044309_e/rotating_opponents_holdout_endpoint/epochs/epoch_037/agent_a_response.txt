def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Prefer collecting immediately.
        imm = 1 if (nx, ny) in set(resources) else 0

        self_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            d_s = manh(nx, ny, rx, ry)
            if d_s < self_best:
                self_best = d_s
            d_o = manh(ox, oy, rx, ry)
            if d_o < opp_best:
                opp_best = d_o

        # Win margin: larger means opponent is farther to the best target vs us.
        margin = opp_best - self_best

        # Tie-break: maximize margin, then minimize our distance, then deterministic ordering.
        key = (imm, margin, -self_best, -nx, -ny, -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return best_move