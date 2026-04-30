def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    # If already on a resource, stay (deterministic).
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order by move list; evaluate all moves.
    best_move = (0, 0)
    best_val = -10**18

    # Weights: encourage fast acquisition and resource competition.
    w_contest = 3.0
    w_op_dist = 0.25

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)

        # If no resources visible, drift away from opponent toward board center.
        if not resources:
            cx, cy = W // 2, H // 2
            val = -cheb(nx, ny, cx, cy) + w_op_dist * d_op
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
            continue

        # Target score: closest resource, but penalize resources opponent can reach sooner/equal.
        target_best = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            contest = 0.0
            if do <= ds:
                # If opponent is closer or equal, steer away from that resource.
                contest = (ds - do) + 1.0
            # Lower is better for ds + penalty; convert to maximize later.
            cand = ds + w_contest * contest
            if cand < target_best:
                target_best = cand

        # Higher score is better: minimize target_best, also slightly prefer being farther from opponent.
        val = -target_best + w_op_dist * d_op
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]