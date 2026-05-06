def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    scored = []
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        scored.append((do - ds, -ds, -rx, -ry, rx, ry))
    scored.sort(reverse=True)
    cand = [(x, y) for _, _, _, _, x, y in scored[:3]]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue

        vals = []
        min_ds = None
        best_adv = -10**9
        for rx, ry in cand:
            ds = manh(nx, ny, rx, ry)
            do = manh(nx, ny, ox, oy)  # not used directly; keep structure minimal
            adv = (manh(nx, ny, rx, ry) * -1)  # placeholder replaced below
            _ = do
            opp_d_next = manh(ox, oy, rx, ry)
            adv = opp_d_next - ds
            vals.append(adv)
            if min_ds is None or ds < min_ds:
                min_ds = ds
            if adv > best_adv:
                best_adv = adv

        # Primary: maximize sum of immediate advantage to top candidates.
        # Secondary: get closer to at least one candidate.
        # Tertiary: reduce distance to the overall best candidate.
        sum_adv = 0
        for v in vals:
            sum_adv += v

        target_rx, target_ry = cand[0] if cand else resources[0]
        key = (sum_adv, -min_ds, -manh(nx, ny, target_rx, target_ry), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move