def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evad" in r) or ("runner" in r) or ("evasion" in r) or (r == "evader")

    self_role = observation.get("self_role") or ""
    opp_role = observation.get("opponent_role") or ""
    self_is_evader = is_evader(self_role)
    opp_is_evader = is_evader(opp_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def predict_opponent_next(myx, myy):
        best = None
        best_val = None
        # Assume opponent chooses a move that maximizes/minimizes our distance based on its role.
        for dxo, dyo in moves:
            nx, ny = ox + dxo, oy + dyo
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, myx, myy)
            val = d if opp_is_evader else -d
            if best is None or val > best_val:
                best = (nx, ny)
                best_val = val
        return best if best is not None else (ox, oy)

    target_ox, target_oy = predict_opponent_next(sx, sy)

    best_move = None
    best_tuple = None
    # If we are pursuer: minimize distance to predicted opponent; if evader: maximize.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, target_ox, target_oy)
        primary = d if self_is_evader else -d
        # Tie-break: prefer non-staying and then earlier moves deterministically.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        tup = (primary, -stay_pen, -abs(nx - w // 2) - abs(ny - h // 2))
        if best_tuple is None or tup > best_tuple:
            best_tuple = tup
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]