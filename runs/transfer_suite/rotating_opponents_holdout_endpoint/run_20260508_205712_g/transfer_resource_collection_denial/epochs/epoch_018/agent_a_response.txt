def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def min_dist(px, py):
        md = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = cheb(px, py, rx, ry)
            if d < md:
                md = d
        return md if md < 10**9 else 10**9

    my_md = min_dist(sx, sy)
    op_md = min_dist(ox, oy)
    deny_mode = my_md > op_md  # behind -> deny; ahead -> collect

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if deny_mode:
            target = None
            best_op_closeness = -10**18
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                dO = cheb(ox, oy, rx, ry)
                # prefer resources opponent can grab soon
                score = -dO
                if score > best_op_closeness:
                    best_op_closeness = score
                    target = (rx, ry)
            tx, ty = target
            dS = cheb(nx, ny, tx, ty)
            dO_now = cheb(ox, oy, tx, ty)
            # maximize our "catch-up" advantage; also slightly prefer moving closer to target
            score = (dO_now - dS) * 1000 - dS
            # if we can potentially become no-worse than opponent, boost a lot
            if dS <= dO_now:
                score += 100000
        else:
            best_collect = 10**18
            tx, ty = resources[0]
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d = cheb(nx, ny, rx, ry)
                if d < best_collect:
                    best_collect = d
                    tx, ty = rx, ry
            score = -best_collect  # greedy collect: minimize our distance to nearest accessible resource
            # small preference for pushing diagonally/forward (break ties deterministically)
            score += -(abs(dx) + abs(dy)) * 0.01

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]