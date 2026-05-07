def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick target maximizing "arrive sooner than opponent" pressure
    tr = observation.get("turns_remaining", 0)
    endgame = tr <= 10

    def best_target_value(x, y):
        best = -10**18
        for r in resources:
            tx, ty = r[0], r[1]
            if (tx, ty) in obstacles: 
                continue
            sd = dist_cheb(x, y, tx, ty)
            od = dist_cheb(ox, oy, tx, ty)
            if sd == 0:
                return 10**12
            # Prefer being strictly earlier; in endgame ignore longer travel
            sooner = od - sd
            rowcol_pen = 2 if (ty == oy or tx == ox) else 0
            slack = (tr / 2.0) if tr else 0
            if endgame:
                val = sooner * 30 - sd * 6 - rowcol_pen * 3
            else:
                val = sooner * 18 - sd * 3 - rowcol_pen * 4 + (od - sd) / (sd + 1)
                val += 0.1 * (slack / (sd + 1))
            if val > best:
                best = val
        return best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    cur_val = best_target_value(sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = best_target_value(nx, ny)
        # Small tie-break: move that most reduces distance to best target
        if sc > best_score or (sc == best_score and abs(dx) + abs(dy) < abs(best_move[0]) + abs(best_move[1])):
            best_score = sc
            best_move = (dx, dy)

    if best_score < cur_val:
        # Ensure some progress towards any reachable resource if all equal/blocked
        best_d = 10**9
        cand = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # distance to nearest resource
            md = 10**9
            for r in resources:
                tx, ty = r[0], r[1]
                if (tx, ty) in obstacles:
                    continue
                d = dist_cheb(nx, ny, tx, ty)
                if d < md: md = d
            if md < best_d:
                best_d = md
                cand = (dx, dy)
        best_move = cand

    return [int(best_move[0]), int(best_move[1])]