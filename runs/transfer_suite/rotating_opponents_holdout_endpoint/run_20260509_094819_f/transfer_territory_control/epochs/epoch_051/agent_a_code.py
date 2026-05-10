def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx = int(sp[0]) if len(sp) > 0 else 0
    sy = int(sp[1]) if len(sp) > 1 else 0

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_pos(x, y):
        target = observation.get("opponent_position") or None
        if target is not None and len(target) >= 2:
            ox, oy = int(target[0]), int(target[1])
        else:
            ox, oy = x, y

        un = observation.get("unclaimed_cells") or []
        if un:
            best = 10**9
            for q in un:
                try:
                    qx, qy = int(q[0]), int(q[1])
                    d = abs(x - qx) + abs(y - qy)
                    if d < best:
                        best = d
                except:
                    pass
            return 1000 - best
        res = observation.get("resources") or []
        if res:
            best = 10**9
            for q in res:
                try:
                    qx, qy = int(q[0]), int(q[1])
                    d = abs(x - qx) + abs(y - qy)
                    if d < best:
                        best = d
                except:
                    pass
            return 100 - best
        # fallback: approach opponent
        return 200 - (abs(x - ox) + abs(y - oy))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = score_pos(nx, ny)
        # deterministic tie-break: prefer staying, then smaller lexicographic
        if v > best_val or (v == best_val and ((dx, dy) == (0, 0) or (dx, dy) < best_move)):
            best_val = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]