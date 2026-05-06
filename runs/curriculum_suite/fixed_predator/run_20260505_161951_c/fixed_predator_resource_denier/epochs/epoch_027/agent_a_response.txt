def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def eval_move(nx, ny):
        d_opp = cheb(nx, ny, ox, oy)
        if not resources:
            return d_opp - (abs(nx - (w - 1)) + abs(ny - (h - 1))) * 0.01
        best_r = None
        best_pref = -10**18
        for rx, ry in resources:
            s = cheb(nx, ny, rx, ry)
            o = cheb(ox, oy, rx, ry)
            pref = (o - s) * 200 - s
            # tiny tie-break to reduce oscillations (prefer increasing resource x then y)
            pref += (rx - nx) * 0.001 + (ry - ny) * 0.0005
            if pref > best_pref:
                best_pref = pref
                best_r = (rx, ry)
        rx, ry = best_r

        # if we can likely secure it first, drive straight; otherwise choose closest good resource
        my_to = cheb(nx, ny, rx, ry)
        opp_to = cheb(ox, oy, rx, ry)
        secure = 1 if opp_to - my_to >= 0 else 0

        # also discourage moves that allow opponent to be closer after our move
        cur_self = cheb(x, y, rx, ry)
        cur_opp = cheb(ox, oy, rx, ry)
        progress = (cur_self - my_to) * (1.0 + 0.5 * secure)
        denial = (d_opp - cheb(x, y, ox, oy)) * 2.0

        # slight center/upper-left bias for stability
        pos_bias = -(abs(nx - 0) + abs(ny - 0)) * 0.001

        return progress + best_pref * 0.02 + denial + pos_bias

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        v = eval_move(nx, ny)
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]
    return [int(best[0]), int(best[1])]