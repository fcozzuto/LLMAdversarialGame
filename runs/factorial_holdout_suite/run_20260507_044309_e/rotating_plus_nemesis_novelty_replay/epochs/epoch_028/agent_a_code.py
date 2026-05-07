def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = None

    def eval_pos(nx, ny):
        # prefer resources we can reach no later than opponent; otherwise minimize opponent lead
        win_count = 0
        best_margin = 10**9
        best_ours = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds <= do:
                win_count += 1
                # larger is better: we want ds much smaller than do
                margin = do - ds
                if margin < best_margin:
                    best_margin = margin
                if ds < best_ours:
                    best_ours = ds
            else:
                # discourage moves that worsen our nearest competition
                margin = do - ds  # negative
                if -margin < best_ours:
                    best_ours = -margin
        if win_count > 0:
            # maximize number of winning resources, then maximize ability to take one soon (small ds)
            # and prefer bigger gaps (do - ds), which corresponds to smaller best_margin? handle:
            # use negative of (min do-ds among winning) to push for larger guaranteed gaps
            gap_score = -best_margin
            return (win_count, gap_score, -best_ours)
        # no direct win: minimize opponent lead over our closest contested resource
        # score with negative sum of leads
        leads = []
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            leads.append(cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry))
        leads.sort(reverse=True)  # most positive lead against us is worst; we want largest negative
        worst = leads[0] if leads else 0
        # also keep ourselves progressing to some resource
        nearest = min(cheb(nx, ny, rx, ry) for rx, ry in resources if (rx, ry) not in obstacles) if any((rx, ry) not in obstacles for rx, ry in resources) else 0
        return (0, -worst, -nearest)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        v = eval_pos(nx, ny)
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            best = (dx, dy)
            bestv = v

    if best is None:
        return [0, 0]
    return [best[0], best[1]]