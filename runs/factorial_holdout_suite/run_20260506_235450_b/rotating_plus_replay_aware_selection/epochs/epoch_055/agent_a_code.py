def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    def pick_target():
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prioritize winning margin, then faster self, then nearer resource
            margin = do - ds
            score = (margin, -ds, -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2))
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        return best[1]

    tx, ty = pick_target()

    # obstacle-aware move: choose step that maximizes race margin to target after move
    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        margin2 = do2 - ds2
        # small nudge: keep moving toward target; avoid getting stuck near obstacles
        toward = -cheb(nx, ny, tx, ty)
        penalty = 0
        for ax, ay in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            axx, ayy = nx + ax, ny + ay
            if not inb(axx, ayy) or (axx, ayy) in obstacles:
                penalty -= 0.05
        val = (margin2, -ds2, toward, penalty)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]