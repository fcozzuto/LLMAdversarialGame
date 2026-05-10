def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, dict):
            x = r.get("x", r.get("pos", [None, None])[0])
            y = r.get("y", r.get("pos", [None, None])[1])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def score_move(mdx, mdy):
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            return -10**9
        if res:
            # Prefer moving closer to the nearest resource; break ties by being farther from opponent.
            best = 10**9
            for rx, ry in res:
                d = max(abs(nx - rx), abs(ny - ry))
                if d < best:
                    best = d
            return -best * 1000 - max(abs(nx - ox), abs(ny - oy))
        # No resources: maximize distance from opponent.
        return max(abs(nx - ox), abs(ny - oy))

    best_val = -10**18
    best_move = (0, 0)
    for mdx, mdy in deltas:
        v = score_move(mdx, mdy)
        if v > best_val:
            best_val = v
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]