def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer resources where we can arrive no later than opponent (tie -> closer).
    # If none, pick best "race" based on distance advantage and closeness.
    best = None
    best_key = None
    for rx, ry in res:
        my_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        lead = my_d - opp_d  # <=0 means we arrive earlier or same time
        dist_bias = my_d
        # small deterministic bias to avoid ties; closer to center slightly preferred
        center_bias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        key = (lead, dist_bias, center_bias)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Local obstacle-aware greedy move toward target; diagonal allowed.
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1),
             (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    # Deterministic tie-break: fixed order as listed.
    best_m = [0, 0]
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        blocked = (nx, ny) in obstacles
        d = abs(tx - nx) + abs(ty - ny)
        # Prefer unblocked, then smaller distance; slight preference to not move if equal
        # (keeps deterministic stability when racing is tight).
        key = (1 if blocked else 0, d, abs(dx) + abs(dy))
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = [dx, dy]
    return [int(best_m[0]), int(best_m[1])]