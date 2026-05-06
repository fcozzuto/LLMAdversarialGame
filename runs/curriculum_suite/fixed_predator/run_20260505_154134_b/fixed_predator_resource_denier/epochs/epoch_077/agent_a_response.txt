def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]
    if resources:
        best = None  # (score, dx, dy)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            # Select a "meaningful" target: among resources, prefer those we can reach earlier,
            # else pick one that least helps the opponent.
            local_best = None
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Higher is better for us:
                # - prefer resources that are closer for us than opponent (od - sd large)
                # - slightly discourage long steps (sd small)
                # - prefer pushing opponent by choosing targets where we are closer now
                score = (od - sd) * 10 - sd
                # deterministic tie-break toward nearer absolute progress for us
                score2 = score * 1000 - cheb(nx, ny, sx, sy)
                if local_best is None or score2 > local_best:
                    local_best = score2
            if local_best is None:
                continue
            # Small bias to reduce oscillations: prefer moving closer to the chosen target set
            # by using overall best achievable advantage from current position
            cur_best_adv = None
            for rx, ry in resources:
                sd0 = cheb(sx, sy, rx, ry)
                od0 = cheb(ox, oy, rx, ry)
                adv = (od0 - sd0) * 10 - sd0
                if cur_best_adv is None or adv > cur_best_adv:
                    cur_best_adv = adv
            # Prefer moves that improve our immediate advantage or that don't worsen it too much
            move_score = local_best + (local_best - cur_best_adv) * 0.5
            if best is None or move_score > best[0] or (move_score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (move_score, dx, dy)
        if best is not None:
            return [int(best[1]), int(best[2])]

    # No resources: head toward center with obstacle avoidance and mild opponent pressure
    tx, ty = w // 2, h // 2
    best = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = -cheb(nx, ny, tx, ty)
        # Tie-break to keep away from opponent corner (predator-style)
        tie = cheb(nx, ny, ox, oy)
        if best is None or (v, -tie) > best:
            best = (v, -tie, dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]