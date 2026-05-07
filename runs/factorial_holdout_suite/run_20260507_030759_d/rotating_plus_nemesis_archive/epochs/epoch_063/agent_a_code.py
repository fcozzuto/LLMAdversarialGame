def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if not resources:
        # Move toward opponent's corner along the dominant axis while avoiding obstacles
        candidates = []
        for dx, dy, nx, ny in legal:
            candidates.append((cheb(nx, ny, w - 1, h - 1), cheb(nx, ny, 0, 0), dx, dy))
        candidates.sort(reverse=False)
        return [candidates[0][2], candidates[0][3]]

    best_move = None
    best_score = None

    for dx, dy, nx, ny in legal:
        local_best_adv = -10**9
        local_best_dist = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # prefer resources we can reach earlier/more
            if adv > local_best_adv or (adv == local_best_adv and sd < local_best_dist):
                local_best_adv = adv
                local_best_dist = sd
        # Prefer tie-breaking toward closer completion to our best resource
        score = (local_best_adv, -local_best_dist)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]