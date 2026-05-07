def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def abs_i(z): 
        return z if z >= 0 else -z

    def cheb(x1, y1, x2, y2):
        dx = abs_i(x1 - x2)
        dy = abs_i(y1 - y2)
        return dx if dx >= dy else dy

    # Pick best target: where we are relatively closer than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        key = (opp_d - self_d, -self_d, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose best move among valid deltas, preferring reduction in distance and blocking obstacles.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        new_self_d = cheb(nx, ny, tx, ty)
        # Also bias towards moving generally toward target even when equally distant.
        toward = abs_i(nx - tx) + abs_i(ny - ty)
        score = (best_key[0] - new_self_d, -toward, -abs_i(dx) - abs_i(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move