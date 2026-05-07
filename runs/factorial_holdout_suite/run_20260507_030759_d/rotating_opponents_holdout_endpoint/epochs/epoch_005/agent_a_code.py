def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer: we should be closer; then shorter our distance; then farther from opponent (proxy); then coords
            key = (sd - od, sd, -od, -rx, -ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1] if best is not None else resources[0]
    else:
        # If no resources, head to a corner away from opponent
        target = (0, 0)
        if ox + oy < w/2 + h/2:
            target = (w - 1, h - 1)
        else:
            target = (0, h - 1) if ox >= oy else (w - 1, 0)

    tx, ty = target
    candidates = []
    opp_gain_weight = 0.05

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dcur = man(sx, sy, tx, ty)
            dnew = man(nx, ny, tx, ty)
            opp_dcur = man(ox, oy, tx, ty)
            opp_dnew = man(ox, oy, tx, ty)  # opponent doesn't move in this choice
            # score: prefer reducing our distance; break ties with keeping ourselves closer relative to opponent
            score = (dnew, dcur - dnew, -opp_dnew, abs(nx - tx) + abs(ny - ty))
            # secondary: slight preference to move away from opponent when equally good
            score = (score[0], score[1], score[2] - opp_gain_weight * man(nx, ny, ox, oy), score[3], dx, dy)
            candidates.append((score, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]