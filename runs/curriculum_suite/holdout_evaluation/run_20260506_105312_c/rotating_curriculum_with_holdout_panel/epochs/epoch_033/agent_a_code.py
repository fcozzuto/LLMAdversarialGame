def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass
    if not resources:
        return [0, 0]

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_my = nearest_dist(sx, sy)
    cur_opp = nearest_dist(ox, oy)
    best = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue
        my_d = nearest_dist(nx, ny)
        opp_d = cur_opp
        if my_d == 0:
            score = 10**8
        else:
            score = (opp_d - my_d) * 1000 - my_d
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]