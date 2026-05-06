def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If no resources, run to grow separation from opponent while staying mobile.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (None, None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = man(nx, ny, ox, oy) * 2 - man(nx, ny, cx, cy)
            if v > best[2] or (v == best[2] and (nx, ny) < best[:2]):
                best = (nx, ny, v)
        return [best[0] - sx, best[1] - sy] if best[0] is not None else [0, 0]

    # Pick the resource where we can get (or keep) the lead: maximize (opp_dist - my_dist).
    # Break ties by prefer nearer resources and toward center.
    best_res = None
    best_res_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        dm = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        center_bias = -0.15 * (man(rx, ry, (w - 1) // 2, (h - 1) // 2))
        edge_bias = -0.05 * (rx in (0, w - 1) or ry in (0, h - 1))
        score = (do - dm) * 5 - dm + center_bias + edge_bias
        if score > best_res_score or (score == best_res_score and (rx, ry) < (best_res[0], best_res[1]) if best_res else True):
            best_res_score = score
            best_res = (rx, ry)

    tx, ty = best_res
    # Then choose the immediate move that maximizes the lead-improvement toward that target,
    # while still keeping the result legal.
    best_move = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_d = man(nx, ny, tx, ty)
        my_d0 = man(sx, sy, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Encourage getting closer; also encourage maintaining/creating advantage vs opponent.
        lead_now = (opp_d - my_d) * 6
        tempo = (my_d0 - my_d) * 3
        # Keep from drifting into edges if opponent is close.
        edge_pen = 2.0 if (nx in (0, w - 1) or ny in (0, h - 1)) else 0.0
        v = lead_now + tempo - edge_pen
        if v > best_move[2] or (v == best_move[2] and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_move = (dx, dy, v)

    return [best_move[0], best_move[1]]