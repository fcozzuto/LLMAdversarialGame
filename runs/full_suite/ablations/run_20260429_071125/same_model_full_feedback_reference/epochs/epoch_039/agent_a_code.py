def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    # If resources exist, pick move that maximizes "earlier-than-opponent" advantage to some resource.
    if resources:
        best_move = (0, 0)
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            my_best = -10**9
            # Score by best prospect resource; secondary preference: proximity to that prospect.
            for rx, ry in resources:
                dm = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                # Being closer than opponent helps; being farther hurts.
                # Use large weight to prioritize "winning" contested resources.
                advantage = (do - dm)  # >0 means we are closer (likely win)
                # Encourage immediate progress with smaller dm as tiebreak.
                s = advantage * 100 - dm
                if s > my_best:
                    my_best = s
            # If no move gets evaluated (all blocked), fall back.
            if best_score is None or my_best > best_score:
                best_score = my_best
                best_move = (dx, dy)
            elif my_best == best_score:
                # Deterministic tie-break: choose lexicographically (dx, dy) after favoring larger advantage already equal
                if (dx, dy) > best_move:
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward center to maximize future access.
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = md(nx, ny, cx, cy)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) > best_move):
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]