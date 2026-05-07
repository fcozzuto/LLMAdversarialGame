def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            ex, ey = int(o[0]), int(o[1])
            if 0 <= ex < w and 0 <= ey < h:
                obstacles.add((ex, ey))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying.
    def tie_key(dx, dy):
        return (abs(dx) + abs(dy), dx + 1, dy + 1)

    best_move = None
    best_score = -10**18

    # Strategic bias: move toward resources closer to our side's "front" (opponent opposite corner).
    front_x = 0 if sx > w - 1 - sx else w - 1
    front_y = 0 if sy > h - 1 - sy else h - 1

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        cur_best = -10**18
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)

            # Lead: we want to arrive no later than opponent; big bonus for lead.
            lead = opd - myd  # positive means we are faster
            arrive_bonus = 50 if lead >= 0 else 0
            # Prefer resources that are less "sweep-like" for opponent: those farther from its current front.
            front_pen = 0
            front_pen += abs(rx - front_x) * 0.2 + abs(ry - front_y) * 0.2

            # If opponent can take it faster, discourage. Also encourage going to nearer targets.
            val = lead * 100 + arrive_bonus * 10 - myd * 2 - front_pen
            if val > cur_best:
                cur_best = val

        # If we can grab something immediately, ensure it dominates.
        if (nx, ny) in resources:
            cur_best += 10000

        if cur_best > best_score or (cur_best == best_score and (best_move is None or tie_key(dx, dy) < tie_key(best_move[0], best_move[1]))):
            best_score = cur_best
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]