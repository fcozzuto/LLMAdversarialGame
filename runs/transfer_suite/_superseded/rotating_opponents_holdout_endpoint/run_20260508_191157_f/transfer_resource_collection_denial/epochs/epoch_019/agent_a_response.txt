def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # baseline: greedily approach a "good" resource, but choose the best immediate move with 1-step lookahead
    best_res = None
    best_val = None
    for r in resources:
        sd = abs(r[0] - sx) + abs(r[1] - sy)
        od = abs(r[0] - ox) + abs(r[1] - oy)
        val = (od - sd, -sd)  # maximize distance advantage, then minimize own distance
        if best_val is None or val > best_val:
            best_val = val
            best_res = r

    tx, ty = best_res[0], best_res[1]

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, grid_w - 1), clamp(sy + dy, 0, grid_h - 1)
        if (nx, ny) in obstacles:
            score = (-10**9, 0)
        else:
            # self distance to nearest resource; also how much it beats opponent
            self_d = min(abs(rx - nx) + abs(ry - ny) for (rx, ry) in resources)
            opp_d = min(abs(rx - nx) + abs(ry - ny) for (rx, ry) in resources for _ in [0])  # unused but keeps structure deterministic

            # exact opp min distance to any resource
            od = min(abs(rx - ox) + abs(ry - oy) for (rx, ry) in resources)

            # favor moving toward target resource strongly, and away from opponent
            to_target = abs(tx - nx) + abs(ty - ny)
            dist_opp = abs(ox - nx) + abs(oy - ny)

            # compute score tuple for deterministic comparison
            score = (
                (od - self_d) * 10 - to_target + dist_opp * 0.1,
                -self_d
            )
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move