def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best_move = None
    best_val = None

    for dx, dy, nx, ny in legal:
        # One-ply: after this move, pick the resource where our "race lead" is largest.
        # Lead = (opp_dist - self_dist). Prefer larger lead; if tie, smaller self_dist;
        # if still tie, smaller opponent_dist (more contested but closer to opponent).
        local_best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            val = (od - sd, -sd, -od)
            if local_best is None or val > local_best:
                local_best = val
        if local_best is None:
            continue
        if best_val is None or local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]