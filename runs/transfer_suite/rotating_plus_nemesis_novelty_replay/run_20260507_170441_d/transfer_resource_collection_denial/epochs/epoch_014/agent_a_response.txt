def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = obstacles
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick best resource where we are relatively closer to collect first
    best = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer myd < opd; then smaller myd; then larger opd; then deterministic tie-break
        key = (myd - opd, myd, -opd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    def obstacle_penalty(x, y):
        p = 0
        for px, py in obst:
            md = man(x, y, px, py)
            if md <= 0:
                p -= 1e6
            elif md == 1:
                p -= 80
            elif md == 2:
                p -= 15
        return p

    # Evaluate one-step moves deterministically
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd_t = man(nx, ny, tx, ty)
        opd_t = man(ox, oy, tx, ty)
        # Encourage moving toward target while keeping advantage over opponent
        score = 200 - myd_t
        score += 0.6 * (opd_t - myd_t)
        # If we can grab a resource immediately, make it dominant
        for rx, ry in resources:
            if nx == rx and ny == ry:
                score += 5000
                break
        # Also discourage moving adjacent to obstacles
        score += obstacle_penalty(nx, ny)
        # Micro-avoid: reduce staying when not best
        if dx == 0 and dy == 0:
            score -= 3
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]