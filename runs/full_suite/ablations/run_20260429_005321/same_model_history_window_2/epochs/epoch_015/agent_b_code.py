def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obst = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        obst.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
            res.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obst_pen(x, y):
        p = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obst:
                p += 1
        return p

    best_delta = (0, 0)
    best_score = -10**18

    # Ensure deterministic tie-break: evaluate in fixed dir order and update only on strict improvement
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            score = -10**15
        else:
            score = -adj_obst_pen(nx, ny) * 3
            if res:
                my_best = 10**9
                gap_best = -10**9
                opp_closest_to_that = 10**9
                for rx, ry in res:
                    md = cheb(nx, ny, rx, ry)
                    od = cheb(ox, oy, rx, ry)
                    gap = od - md  # positive => we are closer than opponent
                    if gap > gap_best or (gap == gap_best and (md < my_best or (md == my_best and od < opp_closest_to_that))):
                        gap_best = gap
                        my_best = md
                        opp_closest_to_that = od
                score += gap_best * 6 - my_best * 1 - opp_closest_to_that * 0.5
            else:
                # No resources: try to avoid opponent by moving to maximize distance
                score += cheb(nx, ny, ox, oy) * 1.5
        if score > best_score:
            best_score = score
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]