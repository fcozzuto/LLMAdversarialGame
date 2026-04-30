def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we're closer; break ties by being closer overall.
            key = (opd - myd, -myd, -(abs(rx - (W // 2)) + abs(ry - (H // 2))), rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: move toward center, slightly away from opponent.
        tx, ty = (W // 2), (H // 2)

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    oppd_now = cheb(sx, sy, ox, oy)
    myd_now = cheb(sx, sy, tx, ty)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in valid:
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        # Primary: approach target
        score = (myd_now - myd) * 1000
        # Competitive: don't give opponent an easier route by moving closer to them
        score += (opd - oppd_now) * 3
        # Avoid getting boxed in by preferring moves that don't increase distance to nearest obstacle.
        if obstacles:
            md_ob = 10**9
            for ax, ay in obstacles:
                dd = cheb(nx, ny, ax, ay)
                if dd < md_ob: md_ob = dd
            score += md_ob
        # If we're already on target, stay put unless opponent can take it immediately.
        if myd == 0 and cheb(ox, oy, tx, ty) <= 1:
            score -= 500
        # Small deterministic tie-break favoring diagonal/forward
        score += (1 if dx != 0 and dy != 0 else 0) + (dx == 0 and dy == 0) * -0.5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]