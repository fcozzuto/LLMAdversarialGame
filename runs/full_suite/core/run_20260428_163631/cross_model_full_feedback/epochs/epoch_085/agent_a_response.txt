def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy); op = (ox, oy)
    best = None
    best_key = None

    # Strategy: for each possible next move, evaluate the best resource target
    # using "margin" = (op dist - my dist). Prefer taking resources where we are closer,
    # and where we also reduce opponent ability (op margin dominance). If none, evade.
    for dx, dy, nx, ny in legal:
        cur_my = (nx, ny)
        if resources:
            local_best = None
            local_key = None
            for rx, ry in resources:
                r = (rx, ry)
                dm = dist(cur_my, r)
                do = dist(op, r)
                # Prefer immediate/near progress, and prefer overtaking opponent.
                margin = do - dm
                # Slightly prefer resources that are not too close to opponent (safer path).
                danger = 1.0 / (1 + do)
                key = (-(margin), dm, danger, rx, ry)
                if local_best is None or key < local_key:
                    local_best = r
                    local_key = key

            rx, ry = local_best
            dm = dist(cur_my, (rx, ry))
            do = dist(op, (rx, ry))
            margin = do - dm
            # Bonus if we can reach the resource no worse than opponent (tie favors us).
            take_bonus = 0 if margin < 0 else 2
            # Primary: maximize margin; then minimize our distance; then minimize opponent distance (to block);
            # then deterministic tie-break by delta.
            score_key = (-margin, dm, do, dx, dy)
            score_key = (score_key[0], score_key[1]-take_bonus, score_key[2], score_key[3], score_key[4])
        else:
            # No resources: maximize distance from opponent with deterministic tie-break.
            dm_op = dist(cur_my, op)
            score_key = (-dm_op, dx, dy)

        if best_key is None or score_key < best_key:
            best_key = score_key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]