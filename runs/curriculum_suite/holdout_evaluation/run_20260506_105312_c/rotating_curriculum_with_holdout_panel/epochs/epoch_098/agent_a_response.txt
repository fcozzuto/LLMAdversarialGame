def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not inb(sx, sy) or (sx, sy) in obs:
        sx, sy = 0, 0
        if (sx, sy) in obs:
            # find any non-obstacle safe cell deterministically
            for yy in range(h):
                for xx in range(w):
                    if (xx, yy) not in obs:
                        sx, sy = xx, yy
                        break
                else:
                    continue
                break

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if resources:
        best_score = -10**18
        best = (0, 0)
        close = man(sx, sy, ox, oy) <= 2
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            res_d = min(man(nx, ny, rx, ry) for rx, ry in resources)
            op_d = man(nx, ny, ox, oy)
            score = -2.0 * res_d + (3.0 if close else 1.2) * op_d
            if res_d == 0:
                score += 1000.0
            key = (score, -dx, -dy)  # deterministic tie-break
            if key > (best_score, -best[0], -best[1]):
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]
    else:
        # No resources visible: maximize distance from opponent deterministically
        best_d = -1
        best = (0, 0)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            op_d = man(nx, ny, ox, oy)
            key = (op_d, -dx, -dy)
            if key > (best_d, -best[0], -best[1]):
                best_d = op_d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]