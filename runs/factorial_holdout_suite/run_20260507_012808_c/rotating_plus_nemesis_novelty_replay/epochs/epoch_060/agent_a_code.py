def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    ti = int(observation.get("turn_index", 0) or 0)
    best = None
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        # Prefer resources I'm closer to; penalize those opponent can reach sooner.
        # Tie-break deterministically with turn/coords.
        value = myd - 0.85 * opd + 0.001 * ((rx * 31 + ry * 17 + ti) % 997)
        if best is None or value < best[0]:
            best = (value, rx, ry)
    _, tx, ty = best

    # Greedy one-step toward target; if blocked, try best available neighbor by same criterion.
    cand = []
    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            myd_next = md(nx, ny, tx, ty)
            # Slightly bias progress vs. distance blow-ups
            score = myd_next + 0.0005 * ((nx * 19 + ny * 23 + ti) % 991)
            cand.append((score, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    return [int(cand[0][1]), int(cand[0][2])]