def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def legal(x, y):
        res = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                res.append((dx, dy, nx, ny))
        return res

    my_legals = legal(sx, sy)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Prefer herding towards the corner opponent is closest to (more reliable for zigzags).
    nearest_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    tcx, tcy = nearest_corner

    best = (10**18, 10**18, 0, 0)
    for dx, dy, nx, ny in my_legals:
        if (nx, ny) == (ox, oy):
            return [dx, dy]  # immediate capture (capture_radius=0)

        opp_legals = legal(ox, oy)
        # Opponent chooses the move that maximizes our distance after their move; tie-break lexicographically.
        worst = (-1, -1, 0, 0)  # (dist, corner_dist, odx, ody) with dist max, corner_dist max
        for odx, ody, nox, noy in opp_legals:
            dist = abs(nx - nox) + abs(ny - noy)
            cd = abs(nox - tcx) + abs(noy - tcy)
            cand = (dist, cd, odx, ody)
            if cand > worst:
                worst = cand

        # We pick our move that minimizes opponent's best response distance; secondary: herding progress.
        my_dist_after = worst[0]
        my_corner_after = abs(nx - tcx) + abs(ny - tcy)
        score = (my_dist_after, my_corner_after, abs(dx) + abs(dy), dx, dy)
        if score < best:
            best = score

    return [best[3], best[4]]