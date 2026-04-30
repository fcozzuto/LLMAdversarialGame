def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_resource(cx, cy):
        if not resources:
            return None
        best = None
        best_key = None
        for rx, ry in resources:
            md = man(cx, cy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources I'm closer to; break ties deterministically by position.
            key = (md - od, md, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target = best_resource(sx, sy)

    if target is None:
        tx, ty = ox, oy
    else:
        tx, ty = target

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if resources:
            # Score by improving my closeness to the chosen "best" resource,
            # and slightly reducing opponent's closeness to any resource.
            myd = man(nx, ny, tx, ty)
            od_best = 10**9
            for rx, ry in resources:
                d = man(ox, oy, rx, ry)
                if d < od_best:
                    od_best = d
            # Prefer moves that move me closer and keep opponent from the best options.
            val = -myd + 0.02 * (od_best)
        else:
            # No resources: head toward opponent.
            val = -man(nx, ny, tx, ty)

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]