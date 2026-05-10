def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(from_x, from_y):
        # maximize (opponent_distance - self_distance); tie-break: smaller self_distance, then closer to opponent
        best = None
        for rx, ry in resources:
            sd = cheb(from_x, from_y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (od - sd, -sd, -od, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[1]

    # If opponent is closer to any resource, bias to one we can contest.
    target = best_target(sx, sy)

    dirs = (-1, 0, 1)
    best_move = (None, -10**9)
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            # Evaluate move towards target; also keep contest margin over opponent.
            sd2 = cheb(nx, ny, target[0], target[1])
            od2 = cheb(ox, oy, target[0], target[1])
            margin = od2 - sd2
            bias = -sd2 - (0 if (nx, ny) == (sx + dx, sy + dy) else 0)
            score = margin * 100 + bias
            if score > best_move[1] or (score == best_move[1] and (dx, dy) < best_move[0]):
                best_move = ((dx, dy), score)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]