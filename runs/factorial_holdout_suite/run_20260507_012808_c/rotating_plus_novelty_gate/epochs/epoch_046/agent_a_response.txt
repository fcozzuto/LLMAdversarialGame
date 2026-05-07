def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else int(sx))
    sy = 0 if sy < 0 else (h - 1 if sy >= h else int(sy))
    ox = 0 if ox < 0 else (w - 1 if ox >= w else int(ox))
    oy = 0 if oy < 0 else (h - 1 if oy >= h else int(oy))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1 - sx, h - 1 - sy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res_list = resources
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Deterministic ordering preference: closer-in and toward opponent side
    def move_pref(dx, dy):
        return (0 if (dx == 0 or dy == 0) else 1, -dx, -dy)

    best = None
    best_score = None

    for dx, dy in sorted(moves, key=lambda m: move_pref(m[0], m[1])):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            # engine will keep us in place if invalid; treat as staying
            nx, ny = sx, sy
        # Evaluate best resource by "capture advantage" (opp slower than us), tie-break by our distance
        local_best = None
        for rx, ry in res_list:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Favor resources we can reach at least as fast as opponent, and then closer ones
            advantage = od - sd
            # Slightly prefer corner-to-corner progress deterministically
            progress = cheb(nx, ny, w - 1, h - 1) - cheb(nx, ny, 0, 0)
            score = (advantage, -sd, -progress)
            if local_best is None or score > local_best:
                local_best = score
        if best_score is None or local_best > best_score:
            best_score = local_best
            best = (dx, dy)

    return [int(best[0]), int(best[1])]