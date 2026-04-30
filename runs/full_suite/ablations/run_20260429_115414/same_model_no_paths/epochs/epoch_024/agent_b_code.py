def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Deterministically move toward opponent while avoiding walls/obstacles
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = -man(nx, ny, ox, oy) - (abs(nx - (w // 2)) + abs(ny - (h // 2))) * 0.001
            if best is None or score > best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Score each move by whether we can reach a resource first vs opponent.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Penalize being adjacent to obstacles to reduce accidental trapping.
        adj_pen = 0
        for bx, by in obstacles:
            if abs(nx - bx) <= 1 and abs(ny - by) <= 1 and (nx, ny) != (bx, by):
                adj_pen += 1

        myd_to_best = 10**9
        score = -0.02 * (abs(nx - ox) + abs(ny - oy))  # slightly prefer keeping distance only when tied
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            myd_to_best = myd if myd < myd_to_best else myd_to_best
            win = opd - myd  # positive means we are closer
            # Strongly prioritize resources we can claim earlier than opponent.
            score += (win * 1.0) - myd * 0.03 - max(0, myd - opd) * 0.25

        # If multiple resources yield similar score, prefer the closest reachable one.
        score -= myd_to_best * 0.005
        score -= adj_pen * 0.08

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]