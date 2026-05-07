def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If standing on a resource (likely collect), stay.
    if (sx, sy) in obst:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    opp_focus = None
    # Simple opponent "pressure": pick nearest resource to opponent to anticipate competition.
    best_od = 10**9
    for rx, ry in resources:
        d = cheb_dist(ox, oy, rx, ry)
        if d < best_od or (d == best_od and (rx, ry) < (opp_focus or (10**9, 10**9))):
            best_od = d
            opp_focus = (rx, ry)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        # Evaluate the move by the best resource we can capture advantageously.
        move_best = -10**18
        for rx, ry in resources:
            my_d = cheb_dist(nx, ny, rx, ry)
            op_d = cheb_dist(ox, oy, rx, ry)
            advantage = op_d - my_d  # positive means we reach earlier
            # Heuristic: strongly prefer positive advantage; break ties by closeness and avoiding opponent's nearest target.
            score = 0
            if advantage > 0:
                score += 1000 * advantage
            else:
                score += 200 * advantage  # still move toward something, but less
            score += -3 * my_d
            if opp_focus == (rx, ry):
                score += -30
            move_best = max(move_best, score)

        # Secondary: if equal, prefer smaller distance to overall best target (deterministic).
        if move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)
        elif move_best == best_score:
            tie_d = cheb_dist(nx, ny, opp_focus[0], opp_focus[1]) if opp_focus else 0
            cur_nx, cur_ny = sx + best_move[0], sy + best_move[1]
            cur_d = cheb_dist(cur_nx, cur_ny, opp_focus[0], opp_focus[1]) if opp_focus else 0
            if tie_d < cur_d:
                best_move = (dx, dy)
            elif tie_d == cur_d:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]