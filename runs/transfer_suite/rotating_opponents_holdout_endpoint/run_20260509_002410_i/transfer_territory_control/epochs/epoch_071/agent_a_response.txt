def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    opp_terr = observation.get("opponent_territory") or []
    cx, cy = w // 2, h // 2

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_key = None

    # Prefer unclaimed: maximize (opp_dist - self_dist), then close, then center-bias.
    for cell in unclaimed:
        x, y = int(cell[0]), int(cell[1])
        if (x, y) in blocked:
            continue
        ds = abs(x - sx) + abs(y - sy)
        do = abs(x - ox) + abs(y - oy)
        reach_adv = do - ds
        k = (-reach_adv, ds, abs(x - cx) + abs(y - cy), x, y)
        if best_key is None or k < best_key:
            best_key = k
            best = (x, y)

    # If nothing, try to counterclaim: minimize how much closer we are than opponent.
    if best is None:
        for cell in opp_terr:
            x, y = int(cell[0]), int(cell[1])
            if (x, y) in blocked:
                continue
            ds = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            reach_adv = do - ds
            k = (-reach_adv, ds, abs(x - cx) + abs(y - cy), x, y)
            if best_key is None or k < best_key:
                best_key = k
                best = (x, y)

    if best is None:
        return [0, 0]

    tx, ty = best

    # Choose one step that reduces distance to target, avoids obstacles.
    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    cur_dist = abs(tx - sx) + abs(ty - sy)
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        # Prefer moves that improve (or keep) distance; tie-break toward center; deterministic.
        improve = nd - cur_dist
        k = (improve, nd, abs(nx - cx) + abs(ny - cy), nx, ny, dx, dy)
        if best_move_key is None or k < best_move_key:
            best_move_key = k
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]