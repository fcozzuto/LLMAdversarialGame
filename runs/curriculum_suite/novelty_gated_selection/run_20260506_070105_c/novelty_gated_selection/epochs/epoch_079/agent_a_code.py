def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            # guard center and keep distance from opponent
            key = (-(dist(nx, ny, cx, cy)), dist(nx, ny, ox, oy), dx, dy)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Choose target resource where we can gain territory vs opponent; then move to increase that advantage.
    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # "static guard" to neutralize nearest-resource: evaluate move by best achievable advantage over opponent.
        move_best = None
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # prefer resources we are closer to, but also avoid giving opponent a huge head start
            adv = (do - ds) - 0.12 * dist(nx, ny, cx, cy)
            # slight preference to break ties by being closer
            key2 = (adv, -ds, -dist(nx, ny, ox, oy), rx, ry)
            if move_best is None or key2 > move_best[0]:
                move_best = (key2, ds, do)
        # tie-break: maximize advantage, then minimize our distance to opponent (indirectly intercept)
        final_key = (move_best[0][0], move_best[0][1], move_best[0][2], -dx * dx - dy * dy, dx, dy)
        if best_key is None or final_key > best_key:
            best_key = final_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]