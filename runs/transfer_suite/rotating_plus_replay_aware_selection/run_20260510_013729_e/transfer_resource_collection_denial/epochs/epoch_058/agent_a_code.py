def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    my_now = (sx, sy)
    opp_now = (ox, oy)

    def best_times(px, py):
        # returns (my_min, opp_min, best_resource for each)
        my_min = 10**9
        opp_min = 10**9
        my_tgt = None
        opp_tgt = None
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < my_min or (ds == my_min and (rx, ry) < my_tgt):
                my_min = ds
                my_tgt = (rx, ry)
            if do < opp_min or (do == opp_min and (rx, ry) < opp_tgt):
                opp_min = do
                opp_tgt = (rx, ry)
        return my_min, opp_min, my_tgt, opp_tgt

    # Baseline global targets
    base_my_min, base_opp_min, base_my_tgt, base_opp_tgt = best_times(sx, sy)

    cand_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_val = -10**30
    best_move = [0, 0]

    tx_opp_time_cache = {}
    for rx, ry in resources:
        tx_opp_time_cache[(rx, ry)] = cheb(ox, oy, rx, ry)

    for dx, dy in cand_dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            # invalid => engine keeps in place, so allow scoring using (sx, sy)
            nx, ny = sx, sy

        my_min, opp_min, my_tgt, opp_tgt = best_times(nx, ny)

        # Main objective: take tempo vs opponent
        tempo = (opp_min - my_min)

        # Capture incentive
        cap = 3.0 if (nx, ny) in resources else 0.0

        # Denial: focus on resource closest to us that the opponent could also reach quickly
        denial = 0.0
        if my_tgt is not None:
            do = tx_opp_time_cache[my_tgt]
            # If opponent is also close, increasing our speed is more valuable
            denial = 1.2 * (do - my_min)  # positive when we can beat their reach to our target
            if do == my_min:
                denial += 0.6  # tight races slightly favor our consolidation

        # Extra: move that reduces opponent's best achievable "advantage"
        # (using difference from baseline as a deterministic directional bias)
        bias = 0.06 * (cheb(nx, ny, base_opp_tgt[0], base_opp_tgt[1]) if base_opp_tgt else 0.0)

        val = 2.4 * tempo + cap + denial + bias

        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move