def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_cells = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_cells.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist2(a, b):
        dx, dy = a[0] - b[0], a[1] - b[1]
        return dx * dx + dy * dy

    center = (cx, cy)
    candidates = []
    for u in unclaimed:
        if u in obs_cells or u in opp_terr:
            continue
        candidates.append(u)
    if candidates:
        target = min(candidates, key=lambda u: dist2((u[0], u[1]), center))
    else:
        target = (int(round(cx)), int(round(cy)))
        if target in obs_cells:
            target = (0, 0)

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    best = (0, 0)
    best_val = -10**18

    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs_cells:
                continue
            move_is_to_opp = (nx, ny) in opp_terr

            dcur = dist2((sx, sy), (int(target[0]), int(target[1])))
            dnew = dist2((nx, ny), (int(target[0]), int(target[1])))
            step_gain = dcur - dnew  # positive if we move closer

            opp_bias = dist2((nx, ny), (ox, oy))
            danger = 0
            if move_is_to_opp:
                danger = 10**9  # avoid immediate flip
            # Prefer advancing toward center while also staying away from opponent
            val = step_gain * 5 + opp_bias * 0.02 - danger
            if val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]