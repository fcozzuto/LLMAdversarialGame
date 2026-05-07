def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target: closest resource; break ties by lower opponent distance (we prioritize stealing races).
    best_t = None
    best_key = None
    for (rx, ry) in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        key = (d_self, -d_opp, (rx + ry) % 8)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_d = cheb(sx, sy, rx, ry)

    # One-step lookahead: minimize distance to target; secondarily avoid moving "away"; avoid obstacles; deterministic tie-break.
    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, rx, ry)
        # Prefer progress; penalize being stuck if not improving.
        score = (d, 0 if d < cur_d else 1, cheb(nx, ny, ox, oy), (nx * 7 + ny) % 11, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_m = (dx, dy)

    # If all non-obstacle in-bounds moves were invalid (rare), allow staying.
    if best_score is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]