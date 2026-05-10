def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = resources[0]
    best_val = -10**18
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        margin = do - ds  # positive => we are closer in turns needed
        # Also prefer resources not immediately monopolized by opponent.
        val = 3 * margin - (ds) - (0 if do == 0 else 0.25 * do)
        # If we are behind, reduce attractiveness unless opponent is extremely close.
        if margin < 0:
            val -= 1.5 * abs(margin)
        if val > best_val:
            best_val = val
            best = (x, y)

    tx, ty = best

    # Local move choice: pick legal step that best reduces distance to target,
    # with a small bias away from being closer to opponent on the target.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                ds2 = cheb(nx, ny, tx, ty)
                do2 = cheb(ox, oy, tx, ty)
                val = -ds2 - 0.15 * do2
                # Slight penalty for moving away from target even if tie.
                if ds2 > cheb(sx, sy, tx, ty):
                    val -= 0.05
                moves.append((val, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (t[0], -t[1], -t[2]), reverse=True)
    return [int(moves[0][1]), int(moves[0][2])]