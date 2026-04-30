def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        return [0, 0]

    best = None
    best_val = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer resources we can reach first; small bias to move along.
        val = ds - 0.6 * do + 0.02 * (rx + ry)
        if best_val is None or val < best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best
    dx0 = 0 if rx == sx else (1 if rx > sx else -1)
    dy0 = 0 if ry == sy else (1 if ry > sy else -1)

    # Candidate preferred deltas: toward target (diagonal if possible), then axis, then stay.
    cand = []
    cand.append((dx0, dy0))
    if dx0 != 0:
        cand.append((dx0, 0))
    if dy0 != 0:
        cand.append((0, dy0))
    cand += [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    # Filter and score candidates by resulting distance to target and survival.
    bestm = (0, 0)
    bestscore = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        sc = dist(nx, ny, rx, ry)
        # Slightly avoid stepping closer to opponent when not improving target distance.
        sc += 0.15 * dist(nx, ny, ox, oy)
        # Prefer diagonal when it doesn't hurt.
        if dx != 0 and dy != 0:
            sc -= 0.05
        if bestscore is None or sc < bestscore:
            bestscore = sc
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]