def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obs:
        try:
            obs_set.add((int(p[0]), int(p[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    resources = observation.get("resources", None)
    targets = resources if resources else []
    best = None
    best_score = None

    # Prefer nearest resource, else move toward opponent.
    if targets:
        ts = []
        for p in targets:
            try:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obs_set:
                    ts.append((x, y))
            except:
                pass
        if ts:
            target = min(ts, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        else:
            target = (ox, oy)
    else:
        target = (ox, oy)

    tx, ty = int(target[0]), int(target[1])
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d1 = abs(nx - tx) + abs(ny - ty)
        d2 = abs(nx - ox) + abs(ny - oy)
        # Lower distance to target is better; small tie-break toward opponent.
        score = (-d1, -d2, dx, dy)
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]
    return best