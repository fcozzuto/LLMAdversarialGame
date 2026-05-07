def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        return max(abs(bx - ax), abs(by - ay))

    def opp_best_next_dist(r_x, r_y):
        best = 10**9
        for mdx, mdy in moves:
            nx, ny = ox + mdx, oy + mdy
            if inb(nx, ny):
                d = cheb(nx, ny, r_x, r_y)
                if d < best:
                    best = d
        return best

    best_move = (0, 0)
    best_score = -10**18
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue
        own_d_best = 10**9
        score_for_move = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = cheb(nsx, nsy, rx, ry)
            ot = cheb(ox, oy, rx, ry)
            opp_next = opp_best_next_dist(rx, ry)

            # Main: only positive advantage if we are strictly closer now
            adv = ot - st
            # Deny: penalize resources where opponent can close to be within our timeline
            deny = 0
            if opp_next <= st:  # opponent can be as fast after its next move
                deny = (st - opp_next + 1) * 50

            # Prefer earlier capture, then larger advantage, then slightly favor central-ish resources
            center_bias = -abs((rx - (w - 1) / 2)) - abs((ry - (h - 1) / 2))
            cand = adv * 200 - st * 8 + center_bias - deny

            # If we can land immediately on resource, strongly prefer
            if st == 0:
                cand += 200000

            if cand > score_for_move:
                score_for_move = cand
                own_d_best = st
        # Mild tie-break: move that reduces our distance to the best candidate resource overall
        score_for_move += -own_d_best
        if score_for_move > best_score:
            best_score = score_for_move
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]