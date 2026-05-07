def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Go toward center to reduce predictability vs opponent
        tx, ty = (w - 1) // 2, (h - 1) // 2
        ddx = tx - sx
        ddy = ty - sy
        return [1 if ddx > 0 else (-1 if ddx < 0 else 0), 1 if ddy > 0 else (-1 if ddy < 0 else 0)]

    # Pick resource that maximizes my advantage; if close, prefer one that blocks opponent
    best = None
    best_key = None
    for rx, ry in resources:
        myd = dist(rx, ry, sx, sy)
        opd = dist(rx, ry, ox, oy)
        # Higher is better: win likelihood first, then speed, then slight tie-break toward staying aligned
        # If myd==opd, prefer resource that is farther from opponent's direction by myd parity proxy.
        key = ((opd - myd), -(myd), -abs((rx - sx) - (ry - sy)), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Greedy move toward target with obstacle avoidance
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nd = dist(tx, ty, nx, ny)
            # penalize moves that let opponent get closer too quickly
            opd_now = dist(tx, ty, ox, oy)
            opp_pen = 0
            # deterministic mild penalty if my move makes me not much closer
            my_now = dist(tx, ty, sx, sy)
            if nd >= my_now:
                opp_pen = 1
            score = (nd, opp_pen, abs(dx) + abs(dy))
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]