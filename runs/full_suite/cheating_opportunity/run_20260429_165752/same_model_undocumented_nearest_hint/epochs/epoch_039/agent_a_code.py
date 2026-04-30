def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if resources:
        # Deterministic tie-break: sort resources once by (x,y)
        resources = sorted(set(resources))

        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Prefer capturing immediate resource; otherwise maximize advantage margin
            if (nx, ny) in set(resources):
                val = 10**9
            else:
                self_best = 10**9
                opp_best = 10**9
                margin_best = -10**18
                # Evaluate best "resource we can beat opponent on"
                for rx, ry in resources:
                    ds = cheb(nx, ny, rx, ry)
                    do = cheb(ox, oy, rx, ry)
                    margin = do - ds  # higher is better
                    if margin > margin_best:
                        margin_best = margin
                        self_best = ds
                        opp_best = do
                    elif margin == margin_best:
                        if ds < self_best or (ds == self_best and do < opp_best):
                            self_best = ds
                            opp_best = do
                # Encourage getting closer even when margins are similar; punish being behind
                val = 2000 * margin_best - self_best + (self_best == 0) * 10000
            # Subtle anti-stagnation: prefer staying only if no other legal move improves
            if (dx, dy) == (0, 0):
                val -= 1
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # No resources: move towards center, avoiding obstacles
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dc = cheb(nx, ny, int(cx), int(cy))
            val = -dc
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]