def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            best_diff = -10**9
            my_best = 10**9
            opp_best = 10**9
            my_near = 10**9
            opp_near = 10**9
            for rx, ry in resources:
                myd = kdist(nx, ny, rx, ry)
                opd = kdist(ox, oy, rx, ry)
                diff = opd - myd
                if diff > best_diff:
                    best_diff = diff
                if myd < my_near:
                    my_near = myd
                    opp_near = opd
                if myd < my_best:
                    my_best = myd
                    opp_best = opd
            myd_opptarget = my_best
            my_near_dist = my_near
            opp_near_dist = opp_near
            safety = kdist(nx, ny, ox, oy)
            key = (best_diff, -safety, -opp_near_dist, -myd_opptarget, -my_near_dist, dx, dy)
        else:
            # No visible resources: maximize distance from opponent to avoid losing races.
            safety = kdist(nx, ny, ox, oy)
            key = (safety, dx, dy)

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]