def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    def cheb(ax, ay, bx, by):
        da = ax - bx
        if da < 0:
            da = -da
        db = ay - by
        if db < 0:
            db = -db
        return da if da >= db else db

    def min_dist_to_resources(px, py):
        md = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < md:
                md = d
        return md

    opp_min = min_dist_to_resources(ox, oy)
    my_opp = cheb(sx, sy, ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            score = -10**12
        else:
            my_min_next = min_dist_to_resources(nx, ny)
            adv = (opp_min - my_min_next)  # want larger advantage
            dist_from_opp = cheb(nx, ny, ox, oy)
            closer_or_farther = dist_from_opp - my_opp
            score = adv * 1000 + closer_or_farther * 3
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]