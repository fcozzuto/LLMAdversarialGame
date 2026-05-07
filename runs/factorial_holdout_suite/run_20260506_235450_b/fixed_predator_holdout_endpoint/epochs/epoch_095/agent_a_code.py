def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def ti(v):
        try:
            return int(v)
        except:
            return 0

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx = ti(sp[0]) if isinstance(sp, (list, tuple)) and len(sp) > 0 else 0
    sy = ti(sp[1]) if isinstance(sp, (list, tuple)) and len(sp) > 1 else 0
    ox = ti(op[0]) if isinstance(op, (list, tuple)) and len(op) > 0 else 0
    oy = ti(op[1]) if isinstance(op, (list, tuple)) and len(op) > 1 else 0

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
        elif isinstance(p, dict):
            x, y = ti(p.get("x")), ti(p.get("y"))
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = ti(r.get("x")), ti(r.get("y"))
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res.append((x, y))
    if not res:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_blocked(x, y):
        return (x, y) in obstacles or x < 0 or x >= w or y < 0 or y >= h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if cell_blocked(nx, ny):
            nx, ny = sx, sy  # deterministic fallback; engine would keep in place
        # Evaluate best target from the hypothetical next position.
        # Score favors winning races: (opp_dist - self_dist), then shorter self_dist, then farther from opponent? (secondary)
        best_for_pos = None
        for rx, ry in res:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            sc = (od - sd, -sd, -(manh(ox, oy, nx, ny)))  # maximize sc lexicographically
            if best_for_pos is None or sc > best_for_pos:
                best_for_pos = sc
        if best_score is None or best_for_pos > best_score:
            best_score = best_for_pos
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]