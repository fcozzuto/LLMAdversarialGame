def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    deltas = [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    opp_moves = []
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny):
            opp_moves.append((nx, ny))
    if not opp_moves:
        opp_moves = [(ox, oy)]

    best = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # If we can capture now, do it.
        if nx == ox and ny == oy:
            return [dx, dy]

        # 1-step minimax: assume opponent moves to maximize our remaining distance.
        worst = -1
        for px, py in opp_moves:
            d = dist2(nx, ny, px, py)
            if d > worst:
                worst = d

        # Tie-break: favor reducing opponent's distance-to-corners (pinning), and moving diagonally.
        corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
        corner_dist = min(abs(cx - ox) + abs(cy - oy) for cx, cy in corners)
        diag = 1 if dx != 0 and dy != 0 else 0
        forward = abs(nx - ox) + abs(ny - oy)

        score = (-worst, -corner_dist, diag, -forward)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]