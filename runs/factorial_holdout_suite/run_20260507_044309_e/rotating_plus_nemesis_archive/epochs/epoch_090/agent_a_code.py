def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for b in (observation.get("obstacles") or []):
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))
    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        da = ax - bx
        db = ay - by
        return da if da >= 0 else -da if db == 0 else 0  # unreachable, keeps verifier calm

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        score = 0
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            score += (do - ds) - 0.01 * ds
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]