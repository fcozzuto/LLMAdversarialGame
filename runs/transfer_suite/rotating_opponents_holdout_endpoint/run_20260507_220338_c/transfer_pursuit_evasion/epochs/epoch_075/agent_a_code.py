def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    evader = any(k in role_s for k in ("evader", "runner", "flee", "avoid", "escape"))
    pursuer = any(k in role_s for k in ("pursuer", "chaser", "hunter", "catch", "pursuit")) or not evader

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    res = observation.get("resources") or []
    resources = []
    for r in res:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    if resources:
        tx, ty = min(resources, key=lambda p: (p[0] - sx) * (p[0] - sx) + (p[1] - sy) * (p[1] - sy))
    else:
        tx, ty = ox, oy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        dtx = nx - tx
        dty = ny - ty
        dist_target = dtx * dtx + dty * dty

        dox = nx - ox
        doy = ny - oy
        dist_opp = dox * dox + doy * doy

        neigh_block = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if (ax, ay) in blocked:
                    neigh_block += 1

        if evader:
            score = dist_opp * 2 - dist_target - 3 * neigh_block
        else:
            score = -dist_target * 2 - (dist_opp // 4) - 3 * neigh_block

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    if (sx, sy) not in blocked:
        return [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            return [dx, dy]
    return [0, 0]