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

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, deterministically maximize distance from opponent while moving legally.
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            cand = (-(d), dx == 0 and dy == 0)  # prefer larger d
            if best is None or cand < best:
                best = cand
                best_mv = [dx, dy]
        return best_mv if best is not None else [0, 0]

    # Race: for each move, choose the resource where we are closest, and the opponent is farthest.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        best_res = None
        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Prefer smaller our_d, then larger opp_d (minimize our_d, maximize opp_d)
            key = (our_d, -opp_d)
            if best_res is None or key < best_res:
                best_res = key

        # Tie-break: if similarly good, prefer increasing distance from opponent.
        opp_dist_after = man(nx, ny, ox, oy)
        cand = (best_res[0], best_res[1], -(opp_dist_after), dx == 0 and dy == 0)
        if best is None or cand < best:
            best = cand
            best_mv = [dx, dy]

    return best_mv if best is not None else [0, 0]