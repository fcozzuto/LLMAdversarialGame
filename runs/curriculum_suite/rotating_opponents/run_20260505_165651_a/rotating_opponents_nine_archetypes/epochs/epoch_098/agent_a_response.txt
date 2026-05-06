def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer resources where we are relatively closer; break ties by closeness and reward farther from opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        tempo = od - sd  # positive means advantage
        # Tie-break: small self distance, large opponent distance, then stable coordinate order
        key = (tempo, -sd, od, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    deltas = [(-1, -1), (1, -1), (-1, 1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    # If we're likely behind, keep pressure by moving along the diagonal "probe" direction too.
    diag_bias = (1 if tx > sx else -1 if tx < sx else 0, 1 if ty > sy else -1 if ty < sy else 0)
    if (ox != tx or oy != ty) and (man(ox, oy, tx, ty) <= man(sx, sy, tx, ty)):
        diag_bias = (diag_bias[0], diag_bias[1])

    best_move = None
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nsd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        # Move quality: reduce our distance; also prefer moves that keep advantage or improve our lead.
        lead_now = nod - nsd
        move_key = (lead_now, -nsd, 0 if (dx, dy) == diag_bias else -1, -abs(nx - tx) - abs(ny - ty))
        if best_move_key is None or move_key > best_move_key:
            best_move_key = move_key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]