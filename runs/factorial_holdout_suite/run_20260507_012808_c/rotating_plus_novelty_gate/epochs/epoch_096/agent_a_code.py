def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or (0, 0)
    o = observation.get("opponent_position") or (0, 0)
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
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

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_target():
        best = None
        for tx, ty in resources:
            ds = md(sx, sy, tx, ty)
            do = md(ox, oy, tx, ty)
            # Prefer resources where we are relatively closer (do - ds large),
            # then prefer closer resources for faster collection.
            key = (do - ds, -ds, tx, ty)
            if best is None or key > best[0]:
                best = (key, tx, ty)
        return best[1], best[2]

    tx, ty = best_target()

    best_move = [0, 0]
    best_val = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            ns = md(nx, ny, tx, ty)
            no = md(ox, oy, tx, ty)

            # Compare progress vs opponent: maximize relative advantage after move.
            # Small bias toward staying nearer to current best target.
            rel = (no - ns)
            val = rel * 100 - ns

            # If a move is adjacent to any resource, give a slight push (collection soon).
            adj = 0
            for rx, ry in resources:
                d = max(abs(rx - nx), abs(ry - ny))
                if d == 0:
                    adj = 5
                    break
                if d == 1:
                    adj = max(adj, 1)
            val += adj

            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move