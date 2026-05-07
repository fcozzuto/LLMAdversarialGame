def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def t(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0:
            dx = -dx
        dy = by - ay
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_mv = (0, 0)
    best_score = None

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue
        score = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ot = t(ox, oy, rx, ry)
            st = t(nsx, nsy, rx, ry)
            # Strongly prefer moves that let us arrive earlier; otherwise minimize lateness.
            s = (ot - st) * 1000 - st
            if st == 0:
                s += 10**9
            score = s if s > score else score
        # Small deterministic tie-break: prefer staying closer to opponent's target by reducing sum distance.
        if best_score is None or score > best_score:
            best_score = score
            best_mv = (mdx, mdy)
        elif score == best_score:
            cur = abs(ox - (sx + mdx)) + abs(oy - (sy + mdy))
            best = abs(ox - (sx + best_mv[0])) + abs(oy - (sy + best_mv[1]))
            if cur < best:
                best_mv = (mdx, mdy)

    return [best_mv[0], best_mv[1]]