def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def king(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Precompute obstacle-adjacency penalty (to choose routes that avoid local clutter)
    adj_pen = {}
    for (ax, ay) in obstacles:
        for dx, dy in moves:
            nx, ny = ax - dx, ay - dy
            if 0 <= nx < w and 0 <= ny < h:
                adj_pen[(nx, ny)] = adj_pen.get((nx, ny), 0) + 1

    best = None  # (primary_score, tie_break, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate by the best contestable resource reachable from (nx,ny)
        best_for_move = None
        for rx, ry in resources:
            myt = king(nx, ny, rx, ry)
            opt = king(ox, oy, rx, ry)
            adv = opt - myt  # >=0 means we are no slower in "king steps"

            # Extra: discourage stepping into obstacle-adjacent tiles when it doesn't help contest
            local = adj_pen.get((nx, ny), 0)
            # Prioritize win/contest, then advantage, then closer overall to resource, then away from opponent
            score = (adv >= 0, adv, -myt, -local, -(abs(rx - ox) + abs(ry - oy)))
            if best_for_move is None or score > best_for_move:
                best_for_move = score

        # If all resources are bad, still choose move that maximizes (adv, closeness) best_for_move
        if best_for_move is None:
            continue
        # Small tie-break to reduce oscillation: prefer staying when equal contest
        stay_bias = 1 if (dx == 0 and dy == 0) else 0
        primary = best_for_move
        tie = (stay_bias, dx, dy)
        cand = (primary, tie, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[2], best[3]]