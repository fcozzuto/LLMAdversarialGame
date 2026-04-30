def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        resources = [(w // 2, h // 2)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Deterministic tie-breaking via ordered move list.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # One-step lookahead: choose move that maximizes (opponent distance advantage) and also moves into
    # "resource lanes" (best next resource) while penalizing getting close to many resources uniformly.
    best_score = -10**18
    best_move = (0, 0)

    # Precompute opponent best response pressure after our move for stability: use current opponent distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_best = 10**9
        opp_best = 10**9
        max_gap = -10**9
        near_count = 0

        for rx, ry in resources:
            dmy = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            if dmy < my_best:
                my_best = dmy
            if dop < opp_best:
                opp_best = dop
            gap = dop - dmy  # positive: resources are relatively closer to us than to opponent
            if gap > max_gap:
                max_gap = gap
            if dmy <= 2:
                near_count += 1

        # Encourage decisive capture pressure: closer to some resource and larger gap.
        score = (max_gap * 100) - (my_best * 5) + (opp_best - my_best) - (near_count * 0.8)

        # Also discourage stepping into squares that are "equally good" for opponent by using our-to-opponent
        # distance interaction (keeps us from drifting into the opponent's best corridor).
        my_to_opp = cheb(nx, ny, ox, oy)
        score -= (7 - (my_to_opp if my_to_opp < 7 else 7)) * 0.6

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Lexicographic tie-break for determinism
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]