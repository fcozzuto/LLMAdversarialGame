def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a structurally different target: prioritize resources on a parity “front” then by relative gain vs opponent.
    front_x = sx if (sy % 2 == 0) else w - 1 - sx
    best_t = None
    best_key = None
    for tx, ty in resources:
        # front preference: resources more aligned with our current scan direction
        front_score = abs(tx - front_x) + (0 if (ty % 2) == (sy % 2) else 1)
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        rel_gain = opd - myd  # larger means we are closer than opponent
        key = (front_score, -rel_gain, myd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer decreasing our distance to target, winning relative race, and keeping distance from opponent (intercept safety).
        rel = opd - myd
        oppdist_next = cheb(nx, ny, ox, oy)
        # Strongly avoid stepping onto cells adjacent to opponent when not improving the race.
        myd_now = cheb(sx, sy, tx, ty)
        race_improve = (myd < myd_now)
        adj_opp = 1 if oppdist_next <= 1 else 0

        v = 1000 * rel - 10 * myd + 3 * oppdist_next + (20 if (nx, ny) == (tx, ty) else 0)
        if adj_opp and not race_improve:
            v -= 500

        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]

    return best