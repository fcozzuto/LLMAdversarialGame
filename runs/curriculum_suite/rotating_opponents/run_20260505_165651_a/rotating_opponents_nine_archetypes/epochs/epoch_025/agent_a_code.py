def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def eval_cell(nx, ny):
        best = (-10**9, 10**9, -10**9)  # (adv, myd, oppd) with max adv, then min myd, then max oppd
        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            oppd = king_dist(ox, oy, rx, ry)
            adv = oppd - myd
            key = (adv, -myd, oppd)
            bkey = (best[0], -best[1], best[2])
            if key > bkey:
                best = (adv, myd, oppd)
        return best  # (adv, myd, oppd)

    best_move = (0, 0)
    best_score = (-10**18, 10**18, -10**18, -1)  # (adv, -myd, oppd, stayflag)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        adv, myd, oppd = eval_cell(nx, ny)
        stayflag = 1 if (dx == 0 and dy == 0) else 0
        score = (adv, -myd, oppd, -stayflag)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]