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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    d_to_opp = cheb(sx, sy, ox, oy)
    best = None
    best_score = -10**18

    # Deterministic tie-break by move ordering (moves list order)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Late-game: drift toward center while staying as far from opponent as possible
        cx, cy = (W - 1) // 2, (H - 1) // 2
        phase = 0
        try:
            phase = int(observation.get("turn_index") or 0)
        except:
            phase = 0

        score = 0
        if resources:
            best_local = -10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer resources where we can arrive earlier (or tie and be closer by potential blocking)
                win_term = 1 if myd <= opd else -1
                # Strongly prioritize near-by, especially when contested
                cand = win_term * (1000 // (1 + myd))
                # Avoid stepping into positions that give opponent an immediate nearer resource
                cand -= (opd - myd) * (2 if myd <= opd else 1)
                # Small center preference to reduce dithering
                cand += (-(abs(nx - cx) + abs(ny - cy))) * 0.01
                if cand > best_local:
                    best_local = cand
            score = best_local
        else:
            score = 50 * cheb(nx, ny, cx, cy) * (-1)  # closer to center
            score += 5 * (cheb(nx, ny, ox, oy))  # farther from opponent

        # Always discourage moving closer to opponent when not improving resource capture
        score += -3 * (cheb(nx, ny, ox, oy) - d_to_opp)

        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]