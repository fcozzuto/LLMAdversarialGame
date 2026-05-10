def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in (observation.get("obstacles") or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res_list.append((x, y))
        elif isinstance(r, dict):
            x, y = r.get("x"), r.get("y")
            if x is not None and y is not None:
                x, y = int(x), int(y)
                if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                    res_list.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_move = deltas[0]
    best_score = None

    seek_resources = True
    if res_list:
        seek_resources = True
    else:
        seek_resources = False

    if seek_resources:
        def target_dist(nx, ny):
            md = None
            for tx, ty in res_list:
                d = dist2(nx, ny, tx, ty)
                if md is None or d < md:
                    md = d
            return md if md is not None else 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            score = target_dist(nx, ny) + 0.01 * dist2(nx, ny, ox, oy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            score = -dist2(nx, ny, ox, oy) + 0.001 * (abs(nx - sx) + abs(ny - sy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    nx, ny = sx + best_move[0], sy + best_move[1]
    if not inside(nx, ny):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best_move