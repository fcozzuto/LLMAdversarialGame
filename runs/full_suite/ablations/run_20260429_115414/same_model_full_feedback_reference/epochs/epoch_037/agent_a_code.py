def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
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

    def manh(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort(key=lambda d: (d[0] * d[0] + d[1] * d[1], d[0], d[1]))

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = manh(nx, ny, ox, oy)

        if resources:
            best_res = None
            best_d = None
            for rx, ry in resources:
                d = manh(nx, ny, rx, ry)
                if best_d is None or d < best_d:
                    best_d = d
                    best_res = (rx, ry)
            # maximize: closer to resources, keep distance from opponent
            score = (-best_d) + 0.25 * d_op
            # mild safety: discourage stepping adjacent to opponent
            if d_op <= 1:
                score -= 2.0
        else:
            # no resources known: head toward opponent if far, otherwise stay safer
            score = 0.15 * d_op if d_op <= 2 else (-0.15 * d_op)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best