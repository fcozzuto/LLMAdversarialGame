def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        bestv, bestm = -10**18, (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -(cheb(nx, ny, cx, cy))  # head to center to stay flexible
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    # evaluate each move by how much it can get ahead of the opponent on some resource
    bestv, bestm = -10**18, (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_best = 10**9
        opp_best = 10**9
        # Also lightly prefer moving toward resources clustered near center
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if md < my_best: my_best = md
            if od < opp_best: opp_best = od

        # primary: maximize advantage (opponent closer is bad)
        # score: (opp nearest distance - my nearest distance), so larger is better
        advantage = opp_best - my_best
        # secondary: break ties toward center to reduce later pathing risk
        center_bias = -cheb(nx, ny, cx, cy) * 0.01

        # tertiary: slight penalty for being adjacent to opponent (can interfere/allow stealing)
        adj_pen = -0.02 * (cheb(nx, ny, ox, oy) == 1)

        v = advantage + center_bias + adj_pen
        if v > bestv:
            bestv, bestm = v, (dx, dy)

    return [bestm[0], bestm[1]]