def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "")
    is_pursuer = ("pursu" in role.lower()) or ("chase" in role.lower()) or ("capt" in role.lower())
    if not is_pursuer:
        is_evader = ("evad" in role.lower()) or ("escap" in role.lower())
        if not is_evader:
            is_evader = True

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x", -1)), int(p.get("y", -1))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def d2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    if is_pursuer:
        best = None
        best_key = None
        for dx, dy, nx, ny in valid:
            dist = d2(nx, ny, ox, oy)
            key = (dist, abs(ox - nx), abs(oy - ny), -(dx == 0) - (dy == 0), moves.index((dx, dy)) if (dx, dy) in moves else 9)
            # simpler deterministic tie-break: use dist then move order
            if best_key is None or key[:1] < best_key[:1] or (key[:1] == best_key[:1] and key[4] < best_key[4]):
                best_key = key
                best = (dx, dy)
        # In case of any weirdness, fallback to first minimal-dist move by order
        if best is None:
            best = min([(dx, dy) for dx, dy, _, _ in valid], key=lambda m: (d2(sx + m[0], sy + m[1], ox, oy), moves.index(m)))
        return [int(best[0]), int(best[1])]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))
    tx, ty = target

    # prefer moves that head toward the chosen corner while increasing distance from pursuer
    best = None
    best_key = None
    for dx, dy, nx, ny in valid:
        step_to_corner = abs(tx - nx) + abs(ty - ny)
        dist_from_p = d2(nx, ny, ox, oy)
        key = (-dist_from_p, step_to_corner, moves.index((dx, dy)))
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]