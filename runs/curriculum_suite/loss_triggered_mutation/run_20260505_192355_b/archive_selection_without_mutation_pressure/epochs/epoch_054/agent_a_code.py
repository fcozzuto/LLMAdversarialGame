def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    def dir_step(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    ox_d = md(sx, sy, ox, oy)

    # pick a target that we can potentially secure: minimize (my_dist - opp_dist) with bias to being closer
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # If opponent can reach much earlier, avoid; otherwise prefer closer-to-us and slightly further from opponent
        key = (od - sd, sd, -od, rx, ry)
        # primary objective: maximize (od - sd), i.e., pick most favorable swing
        # So minimize - (od - sd) == minimize key[0]? Here key[0]=(od-sd); want largest => minimize negative not convenient; invert later
        score = (od - sd) - 0.05 * sd + 0.02 * (ox_d)
        cand = (-(od - sd), sd, od, rx, ry, score)
        if best is None or cand < best:
            best = cand

    _, _, _, tx, ty, _ = best

    # Move one step toward chosen target, but if opponent is very close and could contest, steer away (repel).
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    repulse = 0.0 if ox_d > 3 else (3 - ox_d) * 0.8

    best_val = -10**18
    best_move = (0, 0)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue
        my_to_t = md(nx, ny, tx, ty)
        opp_to_t = md(ox, oy, tx, ty)
        # Since target fixed, estimate whether we improve our relative arrival compared to opponent
        # If we are currently closer, keep heading to target; if opponent is closer, reduce the chance by moving to increase opponent distance.
        val = (opp_to_t - my_to_t) - 0.03 * my_to_t

        if repulse > 0:
            # repel from opponent: prefer increasing distance to opponent
            my_to_opp = md(nx, ny, ox, oy)
            val += repulse * (my_to_opp - ox_d)

        # tiny tie-break toward reducing distance to target directly
        val -= 0.001 * my_to_t

        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]