def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    # Pick a target resource that we are likely to beat (opp closer => low value).
    best_r = None
    best_r_score = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if (rx, ry) in obs:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Large preference for resources where we are closer; tie-break by closeness.
        sc = (od - sd, -sd)
        if best_r_score is None or sc > best_r_score:
            best_r_score = sc
            best_r = (rx, ry)
    if best_r is None:
        best_r = resources[0]
        best_r = (int(best_r[0]), int(best_r[1]))

    tx, ty = best_r
    stay_sd = md(sx, sy, tx, ty)
    best_move = (0, 0)
    best_sc = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        sd = md(nx, ny, tx, ty)
        od = md(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; also prefer moves that keep us beating opponent.
        sc = (od - sd, -(sd), -(abs(nx - tx) + abs(ny - ty)), -((sd > stay_sd) and 1 or 0))
        if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < best_move):
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]