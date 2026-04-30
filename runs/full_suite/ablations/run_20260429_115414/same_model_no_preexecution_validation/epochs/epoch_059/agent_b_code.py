def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obstacles or not (0 <= x < w and 0 <= y < h)

    def near_obst(x, y):
        # mild deterministic "keep-away" from obstacles
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles:
                        return 1
        return 0

    # Choose a target: prefer resources where we can beat the opponent to it; otherwise go closest.
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Encourage "win" routes; slight preference for my-side (x high, y high for agent_b starting corner).
        side = (rx + ry)  # higher is generally more "my-side"
        win_gap = opd - myd  # positive means I can arrive no later
        key = (win_gap, myd, -side, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    # If opponent is very close and we can't beat them (negative/weak gap), prioritize safety by moving away.
    myd0 = cheb(sx, sy, rx, ry)
    opd0 = cheb(ox, oy, rx, ry)
    danger = cheb(sx, sy, ox, oy) <= 2 and (opd0 - myd0) <= 0

    best_move = (0, 0)
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            # Base: reduce distance to target
            nd = cheb(nx, ny, rx, ry)
            base = -nd
            # If danger, increase distance from opponent; else discourage unnecessary retreat from target
            oppd = cheb(nx, ny, ox, oy)
            opp_term = oppd if danger else 0
            # Obstacle keep-away
            obst_term = -2 * near_obst(nx, ny)
            # Small tie-break: prefer moves that keep x and y high (my side) deterministically
            side_term = nx + ny
            score = base + opp_term + obst_term + 0.01 * side_term
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]