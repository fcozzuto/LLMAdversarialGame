def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_resource_score(px, py):
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_me = man(px, py, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Prefer resources we are closer to; otherwise still race but with lower priority.
            # Small bonus for being closer overall to finish sooner.
            advantage = d_opp - d_me
            finish_bias = -d_me
            val = (advantage, finish_bias)
            if best is None or val > best[0]:
                best = (val, (rx, ry), d_me, d_opp)
        return best

    # If standing on a resource (visible), try to stay or make a micro move to remain safe.
    if (sx, sy) in resources:
        return [0, 0]

    # If no visible resources: drift toward the farthest corner from opponent while minimizing obstacle risk.
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # Max distance from opponent, slight preference for moving toward target.
            val = (man(nx, ny, ox, oy), -man(nx, ny, tx, ty))
            if best is None or val > best[0]:
                best = (val, (dx, dy))
        return list(best[1]) if best else [0, 0]

    # Choose the move that maximizes our advantage against the best resource reachable after the move.
    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        br = best_resource_score(nx, ny)
        if br is None:
            continue
        val, (rx, ry), d_me, d_opp = br
        # Convert to a single comparable tuple:
        # 1) our advantage over opponent (higher better)
        # 2) being closer to the chosen resource (lower better)
        # 3) reduce chance of getting blocked by moving away from nearby obstacles
        obstacle_prox = 0
        for (ax, ay) in obstacles:
            if man(nx, ny, ax, ay) <= 1:
                obstacle_prox += 1
        cur = (val[0], -d_me, -obstacle_prox)
        if best_val is None or cur > best_val:
            best_val = cur
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]