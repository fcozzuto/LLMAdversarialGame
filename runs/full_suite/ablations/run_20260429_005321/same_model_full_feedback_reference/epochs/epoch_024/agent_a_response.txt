def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If a resource is adjacent (including current), take it.
    if resources:
        best_adj = None
        for rx, ry in resources:
            if legal(sx, sy) and (sx, sy) == (rx, ry):
                best_adj = (rx, ry)
            if best_adj is None and max(abs(rx - sx), abs(ry - sy)) <= 1:
                best_adj = (rx, ry)
        if best_adj is not None:
            rx, ry = best_adj
            dx = 0 if rx == sx else (1 if rx > sx else -1)
            dy = 0 if ry == sy else (1 if ry > sy else -1)
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]

    # Select target: prioritize resources where we're closer than opponent by a margin.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            margin = od - sd  # positive => we are ahead
            # If ahead, prefer smaller own distance; if behind, prefer breaking ties by distancing from opponent.
            key = (-(margin if margin > 0 else -margin),  # maximize margin positive, otherwise minimize negative margin magnitude
                   0 if margin > 0 else 1,              # ahead targets first
                   sd if margin > 0 else -md(ox, oy, rx, ry),
                   -(rx + ry))  # deterministic tiebreak
            if best_key is None or key < best_key:
                best_key, best = key, (rx, ry)
        tx, ty = best
    else:
        # No resources: move to increase centrality while respecting obstacles.
        tx, ty = w // 2, h // 2

    # Choose best one-step move toward target; also slightly prefer moves that keep away from opponent if target is contested.
    contested = False
    if resources:
        contested = md(ox, oy, tx, ty) <= md(sx, sy, tx, ty)

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_t = md(nx, ny, tx, ty)
        # Score: prefer closer to target; if contested, prefer moving away from opponent.
        score = (d_to_t,
                 -md(ox, oy, nx, ny) if contested else 0)
        # Deterministic tie break by direction ordering already in dirs; so use tuple comparison.
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]