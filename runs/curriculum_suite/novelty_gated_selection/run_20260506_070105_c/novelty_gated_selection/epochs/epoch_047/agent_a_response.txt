def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def p2t(p, default):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    return (x, y)
            except Exception:
                pass
        return default

    sx, sy = p2t(observation.get("self_position", None), (0, 0))
    ox, oy = p2t(observation.get("opponent_position", None), (w - 1, h - 1))

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if tuple(r) not in obstacles]

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def sgn(a):
        return 1 if a > 0 else (-1 if a < 0 else 0)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def diagonal_bias(a, b):
        return abs((a[0] - b[0]) - (a[1] - b[1]))

    def best_target(px, py):
        me = (px, py)
        best = None
        bestv = None
        for rx, ry in resources:
            r = (rx, ry)
            v = (dist(me, r), diagonal_bias(me, r))
            if best is None or v < bestv:
                best = r
                bestv = v
        return best

    opp_target = best_target(ox, oy)

    def opp_next_from_me(px, py, tx, ty):
        # Opponent greedy step toward its chosen target
        return (px + sgn(tx - px), py + sgn(ty - py))

    predicted_opp_next = opp_next_from_me(ox, oy, opp_target[0], opp_target[1])
    predicted_opp_next = (max(0, min(w - 1, predicted_opp_next[0])), max(0, min(h - 1, predicted_opp_next[1])))

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my = (nx, ny)
        my_d_to_opp_next = dist(my, predicted_opp_next)

        # choose resource that I can secure earlier than opponent
        # score: lower is better
        bestv = None
        for rx, ry in resources:
            r = (rx, ry)
            d_me = dist(my, r)
            d_opp = dist((ox, oy), r)
            # If opponent is closer, that resource is less attractive
            v = (d_me - 0.85 * d_opp, diagonal_bias(my, r), d_me)
            if bestv is None or v < bestv:
                bestv = v
        attractiveness = bestv[0]

        # avoid stepping into the opponent's likely next cell
        risk = 0 if my_d_to_opp_next > 0 else -4
        score = (attractiveness, my_d_to_opp_next, risk)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]