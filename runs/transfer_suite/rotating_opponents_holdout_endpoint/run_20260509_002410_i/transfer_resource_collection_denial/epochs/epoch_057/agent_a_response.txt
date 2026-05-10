def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if r and len(r) >= 2:
            rx = int(r[0]); ry = int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                targets.append((rx, ry))
    if not targets:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate after move: aim for resources we can beat opponent on; otherwise disrupt opponent.
        score = 0
        for (rx, ry) in targets:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0: score += 10**6
            # If we can arrive not later than opponent, prioritize strongly by arrival margin and proximity.
            if myd <= opd:
                margin = opd - myd  # >=0
                score += (2000 * margin + (50 - myd))
            else:
                # If opponent is closer, penalize unless we reduce the gap.
                gap = myd - opd  # >=1
                score -= (30 * gap + myd)
                # Small anti-commitment: don't chase far-from-everything bad options.
                score -= 2 * (myd > 3)  # deterministic mild penalty
        # Prefer moves that directly reduce opponent's nearest target distance (disruption).
        opp_best = None
        for (rx, ry) in targets:
            opd = cheb(ox, oy, rx, ry)
            if opp_best is None or opd < opp_best:
                opp_best = opd
        # Deterministic tie-break: slightly favor advancing towards opponent's current nearest.
        if opp_best is not None:
            score += 2 * (opp_best - cheb(nx, ny, ox, oy)) * 0  # keep deterministic but neutral
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]