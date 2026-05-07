def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh
    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (gw // 2), (gh // 2)
        best = [-10**9, 0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty)
            if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = [score, dx, dy]
        return [best[1], best[2]]

    # Pre-rank resources by "race edge": how much closer we are than opponent.
    scored = []
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        edge = dO - dS
        # Prefer nearer resources when edge ties.
        scored.append((edge, -dS, rx, ry))
    scored.sort(reverse=True)
    top = scored[:3]  # small, deterministic focus

    best_val, best_move = -10**18, (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Evaluate the best target after this step.
        val = -10**18
        for edge, neg_dS, rx, ry in top:
            dS2 = cheb(nx, ny, rx, ry)
            dO2 = cheb(ox, oy, rx, ry)
            # Main objective: increase race edge; secondary: reduce self distance.
            step_val = (dO2 - dS2) * 10 - dS2
            # Tiny bias to keep movement deterministic toward improving best target.
            if dS2 == cheb(sx, sy, rx, ry):
                step_val -= 0.25
            if step_val > val:
                val = step_val
        # Also allow immediate collection if we are stepping onto a resource.
        if (nx, ny) in set((r[0], r[1]) for r in resources):
            val += 1000
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]