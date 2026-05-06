def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def res_value(rx, ry):
        selfd = abs(rx - sx) + abs(ry - sy)
        oppd = abs(rx - ox) + abs(ry - oy)
        # Primary: out-approach advantage, Secondary: close to reach
        return (oppd - selfd) * 10 - selfd

    # Deterministic target selection: best perceived value; tie-break by closer to self, then lexicographic.
    best_res = None
    best_v = -10**18
    for rx, ry in resources:
        v = res_value(rx, ry)
        if v > best_v:
            best_v = v
            best_res = (rx, ry)
        elif v == best_v and best_res is not None:
            sd = abs(rx - sx) + abs(ry - sy)
            bsd = abs(best_res[0] - sx) + abs(best_res[1] - sy)
            if sd < bsd or (sd == bsd and (rx, ry) < best_res):
                best_res = (rx, ry)

    tx, ty = best_res

    # Score each move by resulting advantage over that same target; if blocked, fallback to any move with best global advantage.
    best_move = (0, 0)
    best_mscore = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        selfd = abs(nx - tx) + abs(ny - ty)
        oppd = abs(ox - tx) + abs(oy - ty)
        # Also add tiny preference for not moving away from other resources to reduce denial mistakes.
        other_bias = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            od = abs(ox - rx) + abs(oy - ry)
            sd = abs(nx - rx) + abs(ny - ry)
            other_bias += (od - sd)
        mscore = (oppd - selfd) * 20 - selfd + (other_bias * 0.05)
        if mscore > best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)

    # Safety: if all candidate moves blocked (unlikely), stay.
    return [int(best_move[0]), int(best_move[1])]