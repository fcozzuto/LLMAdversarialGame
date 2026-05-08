def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rolestr = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in rolestr for k in ("evader", "escape", "flee", "runner"))
    sc = observation.get("scores", None) or {}
    if isinstance(sc, dict):
        my_score = sc.get("self", sc.get("me", sc.get("player", 0)))
        op_score = sc.get("opponent", sc.get("opp", sc.get("enemy", 0)))
        try:
            my_score = int(my_score)
            op_score = int(op_score)
        except:
            my_score, op_score = 0, 0
    else:
        my_score, op_score = 0, 0
        try:
            my_score = int(sc[0])
            op_score = int(sc[1])
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    chase = (not is_evader) and (my_score < op_score)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if chase:
            val = -d
        else:
            val = d
        # Avoid stepping adjacent to obstacles (small penalty)
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj += 1
        val -= adj * 0.05
        if best_score is None or val > best_score or (val == best_score and (dx, dy) < best):
            best_score = val
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]