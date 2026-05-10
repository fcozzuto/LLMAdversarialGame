def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def score_cell(x, y):
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            # Prefer cells that are closer to an "advantaged" resource; small center bias
            key = (adv, -sd, -(abs((w - 1) / 2 - x) + abs((h - 1) / 2 - y)))
            if best is None or key > best:
                best = key
        return best[0], best[1]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        adv, sd = score_cell(nx, ny)
        # Make immediate progress toward best resource while preventing stepping into bad cells
        key = (adv, -sd, -abs(ox - nx) - abs(oy - ny), -abs((w - 1) / 2 - nx) - abs((h - 1) / 2 - ny), dx * 0 + dy * 0)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]