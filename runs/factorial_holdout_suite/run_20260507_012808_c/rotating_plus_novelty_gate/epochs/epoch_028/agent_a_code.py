def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if w <= 0 or h <= 0:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_score = -10**18

    # Prefer moves that create the largest distance advantage to some resource vs opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        local_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Being able to reach first is primary; also prefer shorter own distance.
            # If we can't beat them, reduce their advantage by moving closer.
            reach_adv = opd - myd  # positive is good
            cell_score = (reach_adv * 1000) - myd

            # Mild anti-collision / keep pressure: if we are already at a resource, strongly prefer it.
            if nx == rx and ny == ry:
                cell_score += 10**6

            if cell_score > local_best:
                local_best = cell_score

        # Tie-break deterministically: prefer smaller own distance to best target, then lexicographic move.
        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)
        elif local_best == best_score:
            # deterministic tie: prefer move with smaller distance to opponent then to self-center
            def tie_val(md):
                mx, my = md
                return (cheb(nx := sx + mx, ny := sy + my, ox, oy), cheb(nx, ny, (w - 1)//2, (h - 1)//2), mx, my)
            if tie_val((dx, dy)) < tie_val(best_move):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]