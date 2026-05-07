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

    def best_target():
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # >0 means we are closer in turns
            # tie-break: prefer more margin, then we should get it sooner
            # then choose target farther from center edges to reduce denier interference variability
            edge_bias = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
            key = (margin, -ds, -do, -edge_bias)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[1]

    tx, ty = best_target()

    # move greedily toward target, but keep considering opponent if our next step makes us lose races
    opp_dist_now = cheb(ox, oy, tx, ty)
    best_move = None
    for dx, dy, nx, ny in legal:
        my_next = cheb(nx, ny, tx, ty)
        margin_next = opp_dist_now - my_next
        # prefer moves that keep positive margin; otherwise still minimize our distance
        key = (margin_next, -my_next, -abs((nx + ny) - (sx + sy)))
        if best_move is None or key > best_move[0]:
            best_move = (key, (dx, dy))
    return [int(best_move[1][0]), int(best_move[1][1])]