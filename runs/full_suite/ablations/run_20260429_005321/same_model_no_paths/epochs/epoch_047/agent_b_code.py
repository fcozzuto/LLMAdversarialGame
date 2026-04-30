def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [0, 0]
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res_sorted = sorted(resources)
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Advantage score: prioritize resources where opponent is not closer,
        # and keep progressing toward some nearby resource.
        score = 0
        nearest_our = 10**9
        nearest_opp = 10**9
        for (rx, ry) in res_sorted:
            d_our = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_our < nearest_our: nearest_our = d_our
            if d_opp < nearest_opp: nearest_opp = d_opp

            adv = d_opp - d_our  # positive means we are closer
            # Strongly reward winning a resource race; softly reward being nearer.
            if adv > 0:
                score += 50 * adv - d_our
            else:
                score += 10 * adv - d_our

        # Prevent getting stuck behind opponent: penalize being globally farther.
        score -= 2 * (nearest_our - nearest_opp)
        # Tie-break deterministically by position then move order.
        tie = (nx, ny, dx, dy)
        if score > best_score or (score == best_score and (best is None or tie < best)):
            best_score = score
            best = tie
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move