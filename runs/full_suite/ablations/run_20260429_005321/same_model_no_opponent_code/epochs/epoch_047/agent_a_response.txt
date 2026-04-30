def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cd(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = -10**18
    best_sd = 10**9
    best_rx, best_ry = 0, 0

    for rx, ry in resources:
        sd = cd(sx, sy, rx, ry)
        od = cd(ox, oy, rx, ry)
        val = (od - sd) * 1000 - sd  # prefer where we are relatively closer
        if val > best_val or (val == best_val and (sd < best_sd or (sd == best_sd and (rx, ry) < (best_rx, best_ry)))):
            best_val = val
            best_sd = sd
            best_rx, best_ry = rx, ry
            best = (rx, ry)

    tx, ty = best_rx, best_ry

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = cd(nx, ny, tx, ty)
            score = -d * 1000 - (1 if (nx == ox and ny == oy) else 0)  # keep chasing target
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]