def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Deterministic order for tie-breaking
    moves = sorted(moves)

    # Prefer capturing resources we can reach no later than opponent, while staying away from obstacles
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # obstacle proximity penalty (discourage stepping near)
        prox = 0
        for ax, ay in obstacles:
            if cheb(nx, ny, ax, ay) <= 1:
                prox += 2 if (nx, ny) == (ax, ay) else 1
        val = -0.1 * prox

        # Evaluate best resource matchup
        best_res = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If we can beat (or tie) opponent, prioritize strongly
            beat = od - sd
            # Small preference for nearer overall
            score = 3.0 * beat - 0.05 * sd
            if score > best_res:
                best_res = score
        val += best_res

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move