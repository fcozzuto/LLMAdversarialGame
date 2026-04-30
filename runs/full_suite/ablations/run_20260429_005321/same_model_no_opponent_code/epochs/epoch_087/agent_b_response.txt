def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    alpha = 0.6  # favor resources farther from opponent
    best_target = None
    best_val = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = ds - alpha * do
        if best_val is None or val < best_val or (val == best_val and (do > cheb(ox, oy, best_target[0], best_target[1]) if best_target else False)):
            best_val = val
            best_target = (rx, ry)

    rx, ry = best_target
    # Choose move that best improves objective toward target while keeping away from opponent and obstacles.
    curr_do = cheb(ox, oy, sx, sy)
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = cheb(nx, ny, rx, ry)
        ndo = cheb(ox, oy, rx, ry)  # opponent-target distance unchanged this turn
        # Prefer smaller ds; if tie, prefer moving that increases our distance from opponent.
        score = nds - alpha * ndo - 0.05 * cheb(nx, ny, ox, oy)
        # Tie-break: keep closer to board center to avoid getting boxed.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += 0.001 * (abs(nx - cx) + abs(ny - cy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move == [0, 0]:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best_move