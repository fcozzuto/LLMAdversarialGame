def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obs = observation.get("obstacles", []) or []
    blocked = set((int(a), int(b)) for a, b in obs)

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    pursuit = ("purs" in self_role) or ("purs" in opponent_role and "evad" not in self_role)
    aim_resource = True

    resources = observation.get("resources", []) or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_list.append((int(r[0]), int(r[1])))
    if not res_list:
        aim_resource = False

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_sc = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        if pursuit:
            sc = -dist
        else:
            sc = dist

        if aim_resource:
            dmin = None
            for rx, ry in res_list:
                d = abs(nx - rx) + abs(ny - ry)
                if dmin is None or d < dmin:
                    dmin = d
            if dmin is not None:
                sc += (-dmin if pursuit else dmin) * 2

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]