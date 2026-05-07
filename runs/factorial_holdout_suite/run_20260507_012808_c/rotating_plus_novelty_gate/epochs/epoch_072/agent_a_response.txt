def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    tr = int(observation.get("turns_remaining") or 0)
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for x, y in resources:
        d_me = dist(sx, sy, x, y)
        d_op = dist(ox, oy, x, y)
        reachable = 0 if d_me <= tr + 2 else 1  # prefer resources we can plausibly reach
        # Main objective: get to resources where we're sooner; otherwise contest where opponent is closest.
        # Key: (reachable penalty, relative advantage, my distance, opp distance)
        key = (reachable, d_me - d_op, d_me, d_op)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
        # Simple local detour: try x-only, y-only, then stay.
        opts = []
        if nx != sx and (nx, sy) not in obstacles and 0 <= nx < w:
            opts.append((nx, sy))
        if ny != sy and (sx, ny) not in obstacles and 0 <= ny < h:
            opts.append((sx, ny))
        for px, py in opts:
            dx2 = 0 if px == sx else (1 if px > sx else -1)
            dy2 = 0 if py == sy else (1 if py > sy else -1)
            return [dx2, dy2]
        return [0, 0]

    return [dx, dy]