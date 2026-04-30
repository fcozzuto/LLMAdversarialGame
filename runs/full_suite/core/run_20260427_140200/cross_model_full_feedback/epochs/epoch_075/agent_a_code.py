def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    bestd = 10**9
    for (rx, ry) in resources:
        d = cheb(mx, my, rx, ry)
        if d < bestd:
            bestd = d
            target = (rx, ry)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not ok(nx, ny):
            continue
        if target is not None:
            d_new = cheb(nx, ny, target[0], target[1])
            d_old = bestd
            approach = d_old - d_new
        else:
            approach = 0

        dist_opp = cheb(nx, ny, ox, oy)
        opp_threat = dist_opp - cheb(mx, my, ox, oy)
        if target is not None and resources:
            on_resource = 1 if (nx, ny) in resources else 0
        else:
            on_resource = 0

        score = 10 * approach + 2 * dist_opp + 20 * on_resource + 3 * (-opp_threat)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]