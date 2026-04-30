def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    # Choose a resource I'm likely to capture first (my_dist - opp_dist minimal).
    best_r = None
    best_key = None
    for rx, ry in resources:
        md = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (md - od, md, -rx, -ry)
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)
    tr_x, tr_y = best_r

    # Evaluate each move using a lookahead proxy:
    # maximize (opp_next_dist - my_next_dist) to my best candidates, and also reduce my dist to target.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_to_target = abs(tr_x - nx) + abs(tr_y - ny)
        # Core proxy: how much closer I can be than the opponent on some resource after this move.
        best_adv = None
        for rx, ry in resources:
            my_d = abs(rx - nx) + abs(ry - ny)
            op_d = abs(rx - ox) + abs(ry - oy)
            adv = op_d - my_d  # higher is better
            if best_adv is None or adv > best_adv:
                best_adv = adv

        # Small bias: avoid moving onto cells adjacent to opponent (likely contested).
        opp_sep = abs(ox - nx) + abs(oy - ny)
        adj_pen = -4 if opp_sep <= 1 else 0

        # Prefer moves that actually make progress toward the target.
        prog = -my_to_target

        score = (best_adv, adj_pen, prog, -abs(dx) - abs(dy), -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move