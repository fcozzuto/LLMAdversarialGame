def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(px, py):
        if not resources:
            return (int((W - 1) / 2), int((H - 1) / 2), 10**9, 0)
        best = None
        for tx, ty in resources:
            myd = cheb(px, py, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer resources where we are clearly closer than opponent.
            adv = opd - myd
            # Primary: maximize advantage; Secondary: minimize our distance; Tertiary: nearer center.
            cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
            center_pen = (tx - cx) * (tx - cx) + (ty - cy) * (ty - cy)
            key = (adv, -myd, -center_pen, -tx, -ty)
            if best is None or key > best[4]:
                best = (tx, ty, myd, opd, key)
        tx, ty, myd, opd, _ = best
        return (tx, ty, myd, opd)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    cur_tx, cur_ty, cur_myd, cur_opd = best_target(sx, sy)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        tx, ty, myd, opd = best_target(nx, ny)
        adv = opd - myd
        # If we are not ahead, slightly prioritize denying by moving toward resources opponent would like.
        deny = 0
        if resources and adv < 0:
            deny = myd - opd
        toward = -cheb(nx, ny, tx, ty)
        # Small bias to keep progressing (avoid dithering).
        progress = -0.01 * ((nx - sx) * (nx - sx) + (ny - sy) * (ny - sy))
        center_pen = -0.001 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        score = 1000 * adv + 10 * toward + 2 * deny + progress + center_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]