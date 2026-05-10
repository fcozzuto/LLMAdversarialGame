def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = (p[0], p[1]) if isinstance(p, (list, tuple)) else (p.get("x", 0), p.get("y", 0))
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < W and 0 <= y < H:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    res = []
    for p in observation.get("resources") or []:
        try:
            x, y = (p[0], p[1]) if isinstance(p, (list, tuple)) else (p.get("x", 0), p.get("y", 0))
            x, y = int(x), int(y)
        except Exception:
            continue
        if inb(x, y):
            res.append((x, y))

    if res:
        tx, ty = min(res, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[0], c[1]))
    else:
        # deterministic fallback: go to center, but bias away from opponent
        cx, cy = (W - 1) // 2, (H - 1) // 2
        dxo = 1 if sx < ox else (-1 if sx > ox else 0)
        dyo = 1 if sy < oy else (-1 if sy > oy else 0)
        tx, ty = cx - dxo, cy - dyo
        tx = max(0, min(W - 1, tx))
        ty = max(0, min(H - 1, ty))

    best = None
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # prefer closer to target; penalize proximity to opponent
            d_target = abs(nx - tx) + abs(ny - ty)
            d_opp = abs(nx - ox) + abs(ny - oy)
            score = (d_target, -d_opp, nx, ny)
            if best is None or score < best_score:
                best = [dx, dy]
                best_score = score

    if best is not None:
        return best

    # last resort: any valid move, deterministic
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            if inb(sx + dx, sy + dy):
                return [dx, dy]
    return [0, 0]