def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king_d(a, b):
        ax, ay = a
        bx, by = b
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da > db else db

    def move_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    if not resources:
        return move_toward(ox, oy)

    # Primary: secure resources where we arrive no later than opponent; prioritize largest time advantage.
    # Secondary: within secure set, prefer minimal our distance, then fixed deterministic ordering.
    # If none secure, race for closest winning race margin, then minimal our distance.
    best = None
    best_key = None
    for t in resources:
        sd = king_d((sx, sy), t)
        od = king_d((ox, oy), t)
        secure = sd <= od
        margin = (od - sd)  # positive means we are faster or tie
        key = (
            1 if secure else 0,      # prefer secure
            margin,                  # higher is better
            -sd,                     # lower sd is better -> use negative
            -(t[0] + 31 * t[1])     # deterministic tie-break
        )
        if best_key is None or key > best_key:
            best_key = key
            best = t

    # Small anti-oscillation: if current position is already at best resource, step toward next-most-available.
    if best[0] == sx and best[1] == sy:
        # Choose the best among resources excluding current cell, deterministically.
        nxt = None
        nxt_key = None
        for t in resources:
            if t == best:
                continue
            sd = king_d((sx, sy), t)
            od = king_d((ox, oy), t)
            secure = sd <= od
            margin = (od - sd)
            key = (1 if secure else 0, margin, -sd, -(t[0] + 31 * t[1]))
            if nxt_key is None or key > nxt_key:
                nxt_key = key
                nxt = t
        if nxt is None:
            return [0, 0]
        return move_toward(nxt[0], nxt[1])

    return move_toward(best[0], best[1])