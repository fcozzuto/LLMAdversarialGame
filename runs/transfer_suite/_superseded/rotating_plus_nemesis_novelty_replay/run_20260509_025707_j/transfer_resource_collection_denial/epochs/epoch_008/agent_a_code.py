def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    tr = observation.get("turns_remaining", 0)
    chase_nearest_weight = 1.0 if tr <= 6 else 0.65  # late-game: secure close wins

    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        min_sd = None
        best_adv = None  # (advantage, -sd)
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if min_sd is None or sd < min_sd:
                min_sd = sd
            adv = od - sd  # positive => we are closer than opponent for this resource
            key = (adv, -sd)
            if best_adv is None or key > best_adv:
                best_adv = key

        adv, neg_sd = best_adv
        sd = -neg_sd
        lead_points = adv
        safety = -0.05 * sd  # slight tie-break toward shorter distance
        # late-game favors nearest available resource; otherwise favors stealable lead
        key = (lead_points * (1.0 - chase_nearest_weight) + sd * chase_nearest_weight,
               -sd, safety, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move