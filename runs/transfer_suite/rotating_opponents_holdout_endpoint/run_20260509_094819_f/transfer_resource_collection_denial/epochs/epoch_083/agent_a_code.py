def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick target that maximizes (opponent_advantage_penalty) => we prefer large (opp_d - self_d)
    ti = int(observation.get("turn_index", 0) or 0)
    best_t = None
    best_key = None
    for (tx, ty) in res:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        key = (od - sd, -sd, (tx + 3 * ty + ti) % 7)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Evaluate next moves: reduce our distance, discourage giving opponent progress.
    best_mv = [0, 0]
    best_mc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        nsd = abs(nx - tx) + abs(ny - ty)
        nod = abs(nx - ox) + abs(ny - oy)

        # Prefer: smaller nsd; larger nod (keep away from opponent); also avoid moves that approach opponent's target
        # by considering opponent distance to our target
        osd_next = abs(tx - ox) + abs(ty - oy)  # baseline opponent distance (static 1-step proxy)
        mc = (nsd, -nod, osd_next, (nx + 5 * ny + ti) % 11)
        if best_mc is None or mc < best_mc:
            best_mc = mc
            best_mv = [dx, dy]

    return best_mv