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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        opp_d = cheb(nx, ny, ox, oy)
        res_d = cheb(nx, ny, resources[0][0], resources[0][1]) if resources else 0
        if resources:
            md = res_d
            for rx, ry in resources[1:]:
                d = cheb(nx, ny, rx, ry)
                if d < md: md = d
            res_d = md

        score = 0
        if resources:
            score += (1000 - 20 * res_d)
        score += (10 * (opp_d >= 2))
        score += 30 if resources and res_d == 0 else 0
        score -= 15 if resources and cheb(sx, sy, resources[0][0], resources[0][1]) == 0 and res_d != 0 else 0
        score -= 30 if opp_d == 1 else 0
        score -= 5 * (1 if dx != 0 and dy != 0 else 0)

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best