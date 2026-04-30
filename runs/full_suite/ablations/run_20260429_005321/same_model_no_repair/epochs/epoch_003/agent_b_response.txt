def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        key = (1 if sd <= od else 0, od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t if best_t is not None else (w // 2, h // 2)

    primary = step_toward(tx, ty)

    def eval_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return None
        sd = man((nx, ny), (tx, ty))
        od = man((ox, oy), (tx, ty))
        # Prefer being at least as close as opponent, otherwise minimize disadvantage.
        closeness_ok = 1 if sd <= od else 0
        # Also encourage reducing opponent advantage globally via resource-relative distance.
        rel = od - sd
        return (closeness_ok, rel, -sd, -abs(nx - rx) - abs(ny - ry) if resources else 0, -dx*dx - dy*dy, dx, dy)

    # Determine a secondary reference point deterministically for tie-breaking.
    rx, ry = (best_t if best_t is not None else (tx, ty))

    candidates = []
    for dx, dy in deltas:
        v = eval_move(dx, dy)
        if v is not None:
            candidates.append(v)
    if not candidates:
        return [0, 0]

    # Try primary first, but still choose best by evaluation deterministically.
    candidates.sort(reverse=True)
    if primary in [(sx + d[0], sy + d[1]) for d in []]:
        pass

    # If primary is valid, prefer it unless it is clearly worse.
    px, py = primary
    pv = eval_move(px, py)
    if pv is not None:
        best = candidates[0]
        # If primary is within top-2 by score, commit to it to reduce oscillation.
        if any(c[:4] == pv[:4] for c in candidates[:2]) or candidates.index(pv) <= 1:
            return [px, py]

    best = candidates[0]
    return [best[-2], best[-1]]