def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources, move to reduce distance to opponent's side (deterministic)
    if not resources:
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            # prefer moving toward center relative to opponent corner
            center_bias = abs((nx - (w - 1 - ox))) + abs((ny - (h - 1 - oy)))
            d = dist((nx, ny), (ox, oy))
            score = (d, center_bias)
            if best is None or score < best[0]:
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose the move that maximizes immediate competitive advantage on the best contested resource.
    # Advantage = (opp_dist - self_dist); also include a small term for how fast we get there.
    best_move = valid[0]
    best_score = None
    targets = resources[:]  # deterministic order
    for dx, dy in sorted(valid):
        nx, ny = sx + dx, sy + dy
        # evaluate best resource from this position
        local_best = None
        for tx, ty in targets:
            self_d = dist((nx, ny), (tx, ty))
            opp_d = dist((ox, oy), (tx, ty))
            # If we're already closer, boost. If not, prefer moves that reduce the gap.
            adv = opp_d - self_d
            # tie-break: prefer resources that are nearer once advantage is equal
            score = (-(adv), self_d, tx, ty)  # minimizing this
            if local_best is None or score < local_best:
                local_best = score
        # Convert local_best back to a maximization-like global score deterministically
        adv_val = -(local_best[0])
        self_d_val = local_best[1]
        # Secondary: avoid stepping into tight positions by preferring moves with more freedom
        freedom = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) not in obstacles:
                freedom += 1
        global_score = (-(adv_val), self_d_val, -freedom, dx, dy)
        if best_score is None or global_score < best_score:
            best_score = global_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]