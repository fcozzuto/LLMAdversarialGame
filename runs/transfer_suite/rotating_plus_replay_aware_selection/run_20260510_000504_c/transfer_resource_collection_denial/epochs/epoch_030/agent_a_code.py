def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obs_set.add((int(q[0]), int(q[1])))
            else:
                x, y = p.get("x"), p.get("y")
                if x is not None and y is not None:
                    obs_set.add((int(x), int(y)))

    res_list = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_list.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                res_list.append((int(q[0]), int(q[1])))
            else:
                x, y = r.get("x"), r.get("y")
                if x is not None and y is not None:
                    res_list.append((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_target():
        if not res_list:
            return None
        best = None
        bestd = 10**9
        for x, y in res_list:
            d = max(abs(sx - x), abs(sy - y))
            if d < bestd:
                bestd, best = d, (x, y)
        return best

    tx, ty = best_target() or (ox, oy)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        dist_self = max(abs(nx - tx), abs(ny - ty))
        dist_opp = max(abs(nx - ox), abs(ny - oy))
        score = -dist_self + 0.1 * dist_opp
        if dx == 0 and dy == 0:
            score -= 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]