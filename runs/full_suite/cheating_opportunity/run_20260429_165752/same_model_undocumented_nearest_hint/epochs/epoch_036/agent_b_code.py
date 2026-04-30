def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                res.append((x, y))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def manh(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    # Pick target: prefer resources where we are closer than opponent, otherwise contest by smallest advantage.
    if res:
        best = res[0]
        bestv = None
        for x, y in res:
            md = manh(sx, sy, x, y)
            od = manh(ox, oy, x, y)
            v = (md - od, md)  # smaller is better
            if bestv is None or v < bestv:
                bestv = v
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = W // 2, H // 2

    # Evaluate moves
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_to = manh(nx, ny, tx, ty)
        d_opp = manh(nx, ny, ox, oy)

        # Encourage moving toward target; avoid getting too close to opponent; slight obstacle/edge stabilization
        edge_pen = (nx == 0) + (nx == W - 1) + (ny == 0) + (ny == H - 1)
        near_opp_pen = 0
        if d_opp <= 1:
            near_opp_pen = 3
        elif d_opp <= 2:
            near_opp_pen = 1

        # If opponent is likely closer to target, try to approach its path: bias moves reducing distance difference
        md_cur = manh(sx, sy, tx, ty)
        od_cur = manh(ox, oy, tx, ty)
        md_next = d_to
        od_next = manh(ox, oy, tx, ty)
        contest_bias = 0
        if md_cur > od_cur:
            contest_bias = (md_cur - od_cur) - (md_next - od_next)

        score = (-d_to) - near_opp_pen - 0.2 * edge_pen + 0.05 * contest_bias

        # Prefer staying only if equally good
        if best_score is None or score > best_score + 1e-9 or (abs(score - best_score) <= 1e-9 and dx == 0 and dy == 0):
            best_score = score
            best_move = [dx, dy]

    return best_move if ok(sx + best_move[0], sy + best_move[1]) else [0, 0]