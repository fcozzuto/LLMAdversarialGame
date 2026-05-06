def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obstacles = set()
    for p in obstacles_list:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_dist(px, py):
        bd = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < bd:
                bd = d
        return bd

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def opp_step(curx, cury):
        best = None  # (dist, dx, dy)
        curd = nearest_dist(curx, cury)
        for dx, dy in deltas:
            nx, ny = curx + dx, cury + dy
            if not valid(nx, ny):
                continue
            nd = nearest_dist(nx, ny)
            # greedy: minimize distance; tie-break deterministically toward smaller dx, then smaller dy
            cand = (nd, dx, dy)
            if best is None or cand < best:
                best = cand
        if best is None:
            return curx, cury
        return curx + best[1], cury + best[2]

    cur_opp_d = nearest_dist(ox, oy)
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = nearest_dist(nx, ny)
        if my_d == 0:
            # ensure we prioritize immediate capture
            return [dx, dy]
        novx, novy = opp_step(ox, oy)
        opp_d_after = nearest_dist(novx, novy)
        # main goal: get closer than opponent, with stronger urgency when opponent is near
        score = (opp_d_after - my_d) * 2000 - my_d * 10 + (cur_opp_d - opp_d_after) * 200
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move