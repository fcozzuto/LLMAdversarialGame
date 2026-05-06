def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs:
        obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def nearest_dist(px, py):
        bd = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < bd:
                bd = d
        return bd

    def nearest_resource(px, py):
        bd = 10**9
        br = resources[0]
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < bd:
                bd = d
                br = (rx, ry)
        return br, bd

    my_cur_d = nearest_dist(sx, sy)
    opp_cur_d = nearest_dist(ox, oy)
    (opp_target_x, opp_target_y), opp_target_d = nearest_resource(ox, oy)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (score, -my_d, -cont_d, dx, dy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue
        my_d = nearest_dist(nx, ny)
        opp_d = opp_cur_d
        if my_d == 0:
            score = 10**8
        else:
            score = (opp_d - my_d) * 1000 - my_d

        cont_d = cheb(nx, ny, opp_target_x, opp_target_y)
        # Tie-breakers: prioritize reducing own nearest distance, then contesting opponent's closest resource
        key = (score, -my_d, -cont_d, dx, dy)
        if best is None or key > best:
            best = key

    return [best[3], best[4]]