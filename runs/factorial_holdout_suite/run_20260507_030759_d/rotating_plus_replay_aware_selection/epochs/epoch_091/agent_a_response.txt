def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def best_target():
        if not resources:
            return None
        best = None
        best_key = None
        for (rx, ry) in resources:
            if (rx, ry) in obstacles:
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (sd - od, sd, -(rx + ry))  # prioritize being closer than opponent
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        # deterministic fallback toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy):
            return [dx, dy]
        if inb(sx + dx, sy):
            return [dx, 0]
        if inb(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    tx, ty = target
    on_res = (sx, sy) == (tx, ty)
    best_move = (0, 0)
    best_val = -10**18

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        val = 0
        if (nsx, nsy) == (tx, ty) and (tx, ty) not in obstacles:
            val += 10**9
        # race value: improve relative closeness to chosen target
        self_d = cheb(nsx, nsy, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        val += (opp_d - self_d) * 1000
        # prevent suicide: keep away from obstacles-adjacent not needed; use distance from opponent for tie-break
        dist_from_opp = cheb(nsx, nsy, ox, oy)
        val += dist_from_opp
        # if already on target, prefer staying
        if on_res and (mdx, mdy) == (0, 0):
            val += 500

        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]