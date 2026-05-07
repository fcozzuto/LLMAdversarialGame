def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        # drift to center deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    best_move = [0, 0]

    # One-step lookahead: maximize best race advantage from the candidate next cell.
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        max_adv = None
        nearest = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - self_d  # positive means we are ahead for that resource
            if max_adv is None or adv > max_adv:
                max_adv = adv
            if nearest is None or self_d < nearest:
                nearest = self_d
        # Prefer: largest advantage; then smaller nearest distance; then deterministic move order
        key = (max_adv, -nearest)
        if best is None or key > best:
            best = key
            best_move = [mdx, mdy]

    if best is None:
        return [0, 0]
    return best_move