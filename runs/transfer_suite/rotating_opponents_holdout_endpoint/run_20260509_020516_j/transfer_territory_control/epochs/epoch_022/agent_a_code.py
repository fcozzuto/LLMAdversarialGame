def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (W - 1, H - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x", -1)), int(p.get("y", -1))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))
        except Exception:
            pass

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    resources = observation.get("resources") or []
    best = None
    if resources:
        for r in resources:
            try:
                tx, ty = int(r[0]), int(r[1])
            except Exception:
                if isinstance(r, dict):
                    tx, ty = int(r.get("x", -1)), int(r.get("y", -1))
                else:
                    continue
            if not (0 <= tx < W and 0 <= ty < H):
                continue
            if (tx, ty) in obs:
                continue
            d = abs(tx - sx) + abs(ty - sy)
            if best is None or d < best[0]:
                best = (d, tx, ty)
    if best is not None:
        _, tx, ty = best
        step_candidates = []
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        step_candidates += [(dx, 0), (0, dy), (dx, dy), (0, 0)]
    else:
        step_candidates = [(0, 0)]

    best_move = None
    best_score = None
    for mdx, mdy in step_candidates:
        if mdx < -1 or mdx > 1 or mdy < -1 or mdy > 1:
            continue
        x, y = sx + mdx, sy + mdy
        if not (0 <= x < W and 0 <= y < H) or (x, y) in obs:
            continue
        # Score: prefer resources (if target known) else maximize distance from opponent; also break ties deterministically.
        if resources and best is not None:
            score = - (abs(tx - x) + abs(ty - y))
        else:
            score = (abs(x - ox) + abs(y - oy))
        score -= 0.001 * (abs(mdx) + abs(mdy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [mdx, mdy]

    if best_move is None:
        for mdx, mdy in dirs:
            x, y = sx + mdx, sy + mdy
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                return [mdx, mdy]
        return [0, 0]
    return best_move