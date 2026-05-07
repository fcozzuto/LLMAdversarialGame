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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    best = None
    best_score = None
    # Evaluate each move by the best resource we can secure from the next position,
    # with strong deterrence if opponent can arrive earlier or equally.
    for dx, dy, nx, ny in legal:
        cur_self_d = dist(nx, ny, ox, oy)
        best_r_score = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Primary: maximize how much earlier we arrive than opponent.
            lead = od - sd
            # If opponent is not behind, heavily penalize (denial pressure).
            deny = 0
            if od <= sd:
                deny = 1000 + (sd - od) * 10
            # Secondary: prefer shorter self distance to that resource.
            # Tertiary: slight bias toward center-ish and coordinate determinism.
            center_bias = abs((rx - (w - 1) / 2)) + abs((ry - (h - 1) / 2))
            tieb = (rx + ry) * 0.001
            score = (lead * 10) - deny - sd - 0.05 * center_bias - tieb
            if best_r_score is None or score > best_r_score:
                best_r_score = score
        # Extra tie-break: prefer moves that reduce distance to our best target indirectly
        # by rewarding smaller self-opponent distance only when close.
        if best_score is None or best_r_score > best_score or (best_r_score == best_score and cur_self_d < dist(sx, sy, ox, oy)):
            best_score = best_r_score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]