def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res_list = [(r[0], r[1]) for r in resources]
    if not res_list:
        # No resources: move to reduce opponent distance (deterministic)
        best = None
        for dx, dy, nx, ny in legal:
            val = (cheb(nx, ny, ox, oy), nx, ny, dx, dy)
            if best is None or val < best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Contest score: prefer resources where we are closer than opponent.
    # Also add slight preference for resources closer to center to keep paths stable.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def center_bias(x, y):
        dx = x - cx
        if dx < 0: dx = -dx
        dy = y - cy
        if dy < 0: dy = -dy
        return dx + dy

    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        # Predict opponent best distance to any resource after one opponent move (upper bound via greedy)
        opp_best = 10**9
        for rex, rey in res_list:
            d0 = cheb(ox, oy, rex, rey)
            d1 = d0
            for odx, ody in moves:
                mx, my = ox + odx, oy + ody
                if inb(mx, my) and (mx, my) not in obst:
                    td = cheb(mx, my, rex, rey)
                    if td < d1: d1 = td
            # take min predicted distance over resources to represent "threat"
            if d1 < opp_best: opp_best = d1

        # Evaluate our best contest outcome for resources from this next position
        best_diff = None
        best_tiebreak = None
        for rex, rey in res_list:
            my_d = cheb(nx, ny, rex, rey)
            opp_d = cheb(ox, oy, rex, rey)
            diff = my_d - opp_d  # negative means we are closer
            # Secondary: prefer closer-to-next-resource and closer-to-center
            t = (diff, my_d, center_bias(rex, rey), rex, rey)
            if best_tiebreak is None or t < best_tiebreak:
                best_tiebreak = t
                best_diff = diff

        # If opponent is globally very near some resource, prioritize preventing immediate access:
        # approximate by pushing our position toward any resource the opponent is already close to.
        # (deterministic weight; no randomness)
        immediate_block = 0
        for rex, rey in res_list:
            if cheb(ox, oy, rex, rey) <= 1:
                # try to get within 1 of those "hot" resources
                my_d = cheb(nx, ny, rex, rey)
                if my_d <= 1:
                    immediate_block -= 2
                else:
                    immediate_block -= 0.5 / (my_d + 1)

        # Global objective: minimize diff (make us closer than opponent), then minimize our distance.
        threat_weight = 1 if opp_best <= 2 else 0.3
        val = (best_tiebreak[0], best_tiebreak[1] + threat_weight * best_tiebreak[2], immediate_block, nx, ny, dx, dy)
        if best_val is None or val < best_val:
            best_val = val