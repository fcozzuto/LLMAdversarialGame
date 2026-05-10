def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res_set = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            res_set.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_key = (-10**18, 10**9, 10**9)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        big = 10**6 if (nx, ny) in res_set else 0
        max_diff = -10**18
        best_myd = 10**9
        best_rx = 0
        best_ry = 0

        for rx, ry in resources:
            rx = int(rx); ry = int(ry)
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            diff = opd - myd
            if (diff > max_diff) or (diff == max_diff and (myd < best_myd or (myd == best_myd and (rx < best_rx or (rx == best_rx and ry < best_ry))))):
                max_diff = diff
                best_myd = myd
                best_rx = rx
                best_ry = ry

        score_key = (big + max_diff, -best_myd, (abs((best_rx - ox)) + abs((best_ry - oy))) if resources else 0)
        if score_key[0] > best_key[0] or (score_key[0] == best_key[0] and (score_key[1] > best_key[1] or (score_key[1] == best_key[1] and score_key[2] < best_key[2]))):
            best_key = score_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]