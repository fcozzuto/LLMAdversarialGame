def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def in_bounds(px, py):
        return 0 <= px < w and 0 <= py < h

    occ = set()
    for p in obstacles:
        if p and len(p) >= 2:
            occ.add((int(p[0]), int(p[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    valid = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and (nx, ny) not in occ:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # Choose target: prefer resources where we're closer than opponent; otherwise nearest among remaining.
    best_t = None
    best_key = None
    for p in resources:
        if not p or len(p) < 2:
            continue
        rx, ry = int(p[0]), int(p[1])
        if not in_bounds(rx, ry):
            continue
        ds = cheb(x, y, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive means we're closer
        # key: prefer positive lead, then smaller ds; then farther from opponent to reduce contest
        key = (0 if lead <= 0 else 1, lead, -cheb(ox, oy, rx, ry), -ds)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t if best_t is not None else (x, y)

    # Move evaluation: go toward target while slightly maximizing distance from opponent; big bonus for collecting.
    best_m = (0, 0, -10**9)
    target_set = set()
    for p in resources:
        if p and len(p) >= 2:
            tx, ty = int(p[0]), int(p[1])
            if in_bounds(tx, ty):
                target_set.add((tx, ty))

    for dx, dy, nx, ny in valid:
        d_target = cheb(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, ox, oy)
        bonus = 3 if (nx, ny) in target_set else 0
        # If opponent is closer to target than we are, prioritize blocking by increasing opponent-target distance.
        cur_ds = cheb(x, y, rx, ry)
        cur_do = cheb(ox, oy, rx, ry)
        block = 0
        if cur_do < cur_ds:
            block = 0.5 * (cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry))
        score = (-d_target) + 0.15 * d_opp + bonus + block
        if score > best_m[2]:
            best_m = (dx, dy, score)

    return [int(best_m[0]), int(best_m[1])]