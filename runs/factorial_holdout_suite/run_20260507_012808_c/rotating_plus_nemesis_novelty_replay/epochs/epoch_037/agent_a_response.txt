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

    def man(a, b, c, d):  # Manhattan
        return abs(a - c) + abs(b - d)

    # Pick a target resource: prefer those I'm closer to than opponent (or at least not far behind)
    best = None
    for (rx, ry) in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        if myd == 0:
            best = (0, rx, ry)
            break
        # Utility: smaller is better
        # Encourage capturing (myd) and deny opponent (opd).
        util = (myd - opd) + 0.35 * myd + 0.02 * (rx + ry)
        if best is None or util < best[0]:
            best = (util, rx, ry)
    if best is None:
        # Deterministic fallback: snake-like sweep biased away from opponent
        tx = (w - 1) if (sy % 2 == 0) else 0
        ty = (h - 1) if (sx % 2 == 0) else 0
        rx, ry = tx, ty
    else:
        rx, ry = best[1], best[2]

    # Evaluate one-step moves with greedy lookahead; avoid obstacles when possible.
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    oppd_cur = man(sx, sy, ox, oy)
    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, rx, ry)
        # If move overshoots poorly, penalize. Also slightly discourage moving toward opponent.
        oppd = man(nx, ny, ox, oy)
        util = myd + 0.15 * (oppd_cur - oppd) + 0.0001 * (nx*31 + ny*17)
        # Tie-break: prefer moves that reduce dx/dy magnitude (more direct), then lower dx,dy order deterministic.
        util += 0.00001 * (abs(dx) + abs(dy))
        if util < best_move[0]:
            best_move = (util, dx, dy)

    return [int(best_move[1]), int(best_move[2])]