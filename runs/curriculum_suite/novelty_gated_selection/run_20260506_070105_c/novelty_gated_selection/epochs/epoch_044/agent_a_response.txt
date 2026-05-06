def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def p2t(p, d):
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    return (x, y)
        except Exception:
            pass
        return d

    sx, sy = p2t(observation.get("self_position", None), (0, 0))
    ox, oy = p2t(observation.get("opponent_position", None), (w - 1, h - 1))
    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if len(r) >= 2 and tuple(r) not in obstacles]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    # Pick a "denial" target: close to opponent relative to us.
    best = None
    best_val = None
    for r in resources:
        ds = md((sx, sy), r)
        do = md((ox, oy), r)
        # prioritize resources near opponent; tie-break slightly toward nearer-to-us to secure pickup
        val = (ds - do)  # smaller => more denial
        sec = ds
        if best_val is None or val < best_val or (val == best_val and sec < md(best, (sx, sy)) if best else True):
            best = r
            best_val = val

    tx, ty = best
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        ns = md((nx, ny), (tx, ty))
        no = md((ox, oy), (tx, ty))

        # Score: minimize our distance to target, but also maximize our advantage (closer than opponent)
        adv = no - ns  # positive means we are closer than opponent
        # Small bias to progress toward target direction (break ties deterministically)
        dir_bias = abs(nx - tx) + abs(ny - ty)
        score = (adv, -ns, -dir_bias)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]