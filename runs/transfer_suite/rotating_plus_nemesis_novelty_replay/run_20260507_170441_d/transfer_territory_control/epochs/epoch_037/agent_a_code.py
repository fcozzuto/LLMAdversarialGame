def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
    except:
        w = 8
    try:
        h = int(h)
    except:
        h = 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
            unclaimed.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = (0, 0)
    bestv = None

    if unclaimed:
        # choose closest unclaimed cell target (deterministic tie-break)
        best_t = None
        best_td = None
        for x, y in unclaimed:
            d = abs(x - sx) + abs(y - sy)
            if best_td is None or d < best_td or (d == best_td and (x, y) < best_t):
                best_td = d
                best_t = (x, y)
        tx, ty = best_t
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                continue
            nd = abs(tx - nx) + abs(ty - ny)
            v = nd * 10 - (abs(ox - nx) + abs(oy - ny))
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        if bestv is None:
            return [0, 0]
        return [best[0], best[1]]

    # otherwise: move toward opponent, avoiding obstacles
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        d = abs(ox - nx) + abs(oy - ny)
        if bestd is None or d < bestd or (d == bestd and (dx, dy) < best):
            bestd = d
            best = (dx, dy)
    return [best[0], best[1]] if bestd is not None else [0, 0]