def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    # Heuristic: pick move that maximizes advantage to a resource that we can beat (or at least contest),
    # with a small penalty for giving the opponent a closer route next turn.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_here = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer after the move; tie-break toward smaller self distance.
            adv = do - ds
            # If opponent is already closer, reduce but still allow if ds is very small (resource imminent).
            val = (adv, -ds)
            if best_here is None or val > best_here:
                best_here = val
        # Extra anti-zerg: if we are moving away from all resources (common failure), penalize.
        # Compare current best to next-step best.
        cur_best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            val = (adv, -ds)
            if cur_best is None or val > cur_best:
                cur_best = val
        away_penalty = 0
        if cur_best is not None and best_here is not None and best_here < cur_best:
            away_penalty = 1
        final = (best_here[0], best_here[1] - away_penalty)
        if best_val is None or final > best_val:
            best_val = final
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]