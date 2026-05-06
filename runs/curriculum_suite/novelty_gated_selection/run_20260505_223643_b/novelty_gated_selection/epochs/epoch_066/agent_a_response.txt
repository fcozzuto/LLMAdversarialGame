def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best_score = None
    best_move = [0, 0]
    cur_dist_to_op = cheb(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0.0
        new_dist_to_op = cheb(nx, ny, ox, oy)
        score += (new_dist_to_op - cur_dist_to_op) * 0.8  # discourage being pulled in by denier

        for rx, ry in resources:
            myd_next = cheb(nx, ny, rx, ry)
            opd_now = cheb(ox, oy, rx, ry)
            myd_cur = cheb(sx, sy, rx, ry)

            if myd_next == 0:
                score += 500.0
                continue

            closer = myd_cur - myd_next
            score += closer * 8.0 / (1 + myd_next)

            diff = opd_now - myd_next
            if diff > 0:
                score += (20.0 * diff) / (1 + myd_next)  # position so we reach earlier
            elif diff < 0:
                score -= (18.0 * (-diff)) / (1 + myd_next)  # avoid races we lose

            # mild bias toward resources not blocked by "being behind" opponent
            score += 2.0 / (1 + myd_next)

        if best_score is None or score > best_score + 1e-9:
            best_score = score
            best_move = [dx, dy]
        elif best_score is not None and abs(score - best_score) <= 1e-9:
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return best_move