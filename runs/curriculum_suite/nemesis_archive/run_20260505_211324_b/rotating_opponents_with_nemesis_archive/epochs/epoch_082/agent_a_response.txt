def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in moves:
            sc = -md(nx, ny, tx, ty)
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Prefer resources where we are strictly closer than opponent; otherwise minimize disadvantage.
    best = None
    for dx, dy, nx, ny in moves:
        # If stepping onto a resource, huge value.
        score = 0
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) == 2):
                continue
            rx, ry = r[0], r[1]
            if not (isinstance(rx, int) and isinstance(ry, int)):
                continue
            if (rx, ry) in obs:
                continue
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer
            if myd == 0:
                score = 10_000
                break
            # focus on best target from this move
            gain = adv * 50 - myd
            if score == 0 or gain > score:
                score = gain
        # small tie-break: avoid getting too close to opponent unless it helps
        score += -md(nx, ny, ox, oy) * 1
        if best is None or score > best[0]:
            best = (score, dx, dy)
        elif score == best[0]:
            # deterministic tie-break: prefer dx closer to 0, then dy closer to 0
            if abs(dx) + abs(dy) < abs(best[1]) + abs(best[2]):
                best = (score, dx, dy)

    return [int(best[1]), int(best[2])]