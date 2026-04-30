def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    res_list = observation.get("resources", [])
    obst = set((p[0], p[1]) for p in obstacles)
    resources = set((p[0], p[1]) for p in res_list)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a single "best" resource to race/deny deterministically (closest to us, tie by coords).
    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            key = (d, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        rx, ry = best_r
    else:
        rx, ry = ox, oy

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        if (nx, ny) in resources:
            score = 1e6  # collecting is best
        else:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Denial: after our move, we want to be much closer to the target than the opponent.
            # Also keep some distance from opponent to avoid being cornered.
            opp_dist_from_me = cheb(nx, ny, ox, oy)

            # Secondary: also consider how close we are to any remaining resource.
            # (Lightweight: compute min distance to a small set around the board edges and target.)
            min_res_d = my_d
            if resources:
                for tx, ty in ((rx, ry), (0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
                    if (tx, ty) in resources:
                        d2 = cheb(nx, ny, tx, ty)
                        if d2 < min_res_d:
                            min_res_d = d2

            score = (-my_d) + (0.9 * (opp_d - my_d)) + (0.08 * opp_dist_from_me) + (-0.12 * min_res_d)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Deterministic tiebreaker: prefer moves that reduce distance to the target, then smaller dx/dy tuple.
            cur_my_d = cheb(sx + best_move[0], sy + best_move[1], rx, ry) if (rx is not None) else 0
            cand_my_d = cheb(nx, ny, rx, ry) if (rx is not None) else 0
            if cand_my_d < cur_my_d or (cand_my_d == cur_my_d and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]