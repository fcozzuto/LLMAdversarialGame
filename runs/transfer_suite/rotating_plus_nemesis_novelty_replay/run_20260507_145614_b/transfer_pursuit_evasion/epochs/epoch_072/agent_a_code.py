def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    corners = ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**30

    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        if nx == ox and ny == oy:
            return [dxm, dym]

        dist_opp = d2(nx, ny, ox, oy)
        if res:
            md = 10**18
            for rx, ry in res:
                v = d2(nx, ny, rx, ry)
                if v < md:
                    md = v
            score = dist_opp * 1000 - md
        else:
            score = dist_opp * 1000
            if (nx, ny) in corners:
                score += 10

        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]