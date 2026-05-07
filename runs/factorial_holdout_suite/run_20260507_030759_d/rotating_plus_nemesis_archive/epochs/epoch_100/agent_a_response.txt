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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If no resources, head for center/corner deterministically with obstacle avoidance
    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = manh(nx, ny, tx, ty)
                if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                    best = (d, dx, dy)
        return [best[1], best[2]]

    # Choose move by maximizing "advantage" from next position; prefer resources you can outpace
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        local_best = -10**18
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            # Larger is better: (opponent distance - my distance), then smaller my distance
            score = (od - sd) * 100 - sd
            if score > local_best:
                local_best = score
        # Tie-break deterministically by lexicographic move
        if local_best > best_score or (local_best == best_score and (dx, dy) < best_move):
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]