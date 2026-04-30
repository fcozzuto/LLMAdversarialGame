def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            res.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)

    best_move = (0, 0)
    best_score = -10**18

    if not res:
        tx = (w - 1) if ox > sx else 0
        ty = (h - 1) if oy > sy else 0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            score = -dist((nx, ny), (tx, ty)) - 0.05 * dist((nx, ny), opp)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        me = (nx, ny)
        score = 0
        for r in res:
            dmy = dist(me, r)
            dop = dist(opp, r)
            score += 1.0 / (1 + dmy) - 0.6 / (1 + dop)
        score -= 0.03 * dist(me, opp)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]