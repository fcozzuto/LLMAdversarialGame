def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda m: (abs(m[0]) + abs(m[1]) != 0, m[0], m[1]))  # deterministic bias toward smaller moves

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Score this move by the best resource we can potentially claim next (advantage vs opponent).
        local_best = -10**9
        local_tiebreak = 10**9
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            advantage = opp_d - self_d
            # Prefer resources that we can reach not much later than opponent, but also progress.
            val = advantage * 100 - self_d
            if val > local_best or (val == local_best and self_d < local_tiebreak):
                local_best = val
                local_tiebreak = self_d

        # Extra tie-break: avoid moving away from the most valuable direction.
        if local_best is None:
            continue
        if best_score is None or local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)
        elif local_best == best_score:
            # Prefer move that reduces distance to the single best target by advantage.
            # Compute quick approximate: compare distance to the resource with max (opp_d - self_d) from current pos.
            cur_best = None
            cur_score = -10**9
            for rx, ry in resources:
                adv = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
                if adv > cur_score:
                    cur_score = adv
                    cur_best = (rx, ry)
            crx, cry = cur_best
            cur_dist_new = cheb(nx, ny, crx, cry)
            nx2, ny2 = sx + best_move[0], sy + best_move[1]
            cur_dist_old = cheb(nx2, ny2, crx, cry)
            if cur_dist_new < cur_dist_old:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]