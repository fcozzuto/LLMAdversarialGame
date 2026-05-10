def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_target = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        adv = do - ds  # positive => we are closer
        # Strategic change: contest diagonal alignment instead of same-row.
        diag_contest = 1 if abs(rx - ox) == abs(ry - oy) else 0
        col_contest = 1 if rx == ox else 0
        # Prefer resources that we can reach before/around opponent and that "fit" diagonal shadowing.
        key = (-(adv + 0.6 * diag_contest + 0.3 * col_contest), ds, rx, ry)
        if best_target is None or key < best_target[0]:
            best_target = (key, (rx, ry))
    tx, ty = best_target[1]

    opp_dist_pref = 0
    if abs(tx - sx) + abs(ty - sy) > 0:
        # Small bias: if we are not already ahead, avoid getting too close to opponent.
        ds0 = abs(tx - sx) + abs(ty - sy)
        do0 = abs(tx - ox) + abs(ty - oy)
        opp_dist_pref = 0.7 if do0 <= ds0 else 0.0

    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dtx = abs(tx - nx) + abs(ty - ny)
        dcur = abs(tx - sx) + abs(ty - sy)
        # Favor progress toward target, but keep separation when trailing.
        dop = abs(nx - ox) + abs(ny - oy)
        progress = dcur - dtx
        # If next is a resource, strongly prefer it.
        is_resource = 1 if (nx, ny) in set(tuple(r) for r in resources) else 0
        key = (-(is_resource * 10 + progress), dtx + opp_dist_pref * (1 / (dop + 1)))
        if best_move is None or key < best_move[0]:
            best_move = (key, (dx, dy))

    return list(best_move[1]) if best_move is not None else [0, 0]