def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    res = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    if not res:
        # deterministic fallback: move toward center while avoiding obstacles
        cx, cy = (W - 1) // 2, (H - 1) // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target resource we can reach with a margin over the opponent
    best_target = res[0]
    best_margin = -10**18
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = (do - ds) * 3 - ds  # prefer being closer by a lot; break ties toward nearer
        if margin > best_margin or (margin == best_margin and (rx, ry) < best_target):
            best_margin = margin
            best_target = (rx, ry)

    rx, ry = best_target
    # Evaluate each move: prioritize reducing our distance, keep opponent from gaining too much
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds1 = cheb(nx, ny, rx, ry)
        do1 = cheb(ox, oy, rx, ry)
        # deterministic tie-breaker: lexicographic move
        # value: lower ds1 is better; penalize if our move lets opponent relatively "catch up"
        val = (best_margin + (do1 - ds1) * 2) - ds1
        val -= 0.5 * (abs(nx - rx) + abs(ny - ry)) * 0.01
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]