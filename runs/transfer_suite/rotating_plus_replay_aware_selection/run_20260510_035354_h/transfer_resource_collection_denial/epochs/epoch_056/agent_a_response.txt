def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tx, ty = None, None
    best = None
    for (rx, ry) in res:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer resources where we are not behind; then maximize lead and closeness.
        lead = od - sd
        score = (1 if lead >= 0 else 0, lead, -sd, -rx, -ry)
        if best is None or score > best:
            best = score
            tx, ty = rx, ry

    best_move = [0, 0]
    best_mscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        nd = dist((nx, ny), (tx, ty))
        odi = dist((ox, oy), (tx, ty))
        # Greedy toward target; if tie, reduce opponent lead; avoid dead movement.
        mscore = (0 if (dx == 0 and dy == 0) else 1, odi - nd, -nd, -abs(nx - tx) - abs(ny - ty), -nx, -ny)
        if best_mscore is None or mscore > best_mscore:
            best_mscore = mscore
            best_move = [dx, dy]

    return best_move if best_mscore is not None else [0, 0]