def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = observation.get("resources") or []
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax + ay

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    # If no immediate objective, bias toward center to avoid getting pinned.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if resources:
        targets = [tuple(r) for r in resources]
    elif unclaimed:
        targets = list(unclaimed)
    elif opp_terr:
        targets = list(opp_terr)
    else:
        targets = [(int(round(cx)), int(round(cy)))]

    best = None
    # Score candidate move: prefer entering unclaimed/opponent; otherwise closest to best target; also prefer center.
    for dx, dy, nx, ny in moves:
        on_unclaimed = 1 if (nx, ny) in unclaimed else 0
        on_opp = 1 if (nx, ny) in opp_terr else 0

        dmin = 10**9
        for tx, ty in targets[:40]:
            d = manhattan(nx, ny, tx, ty)
            if d < dmin:
                dmin = d
        center_dist = abs(nx - cx) + abs(ny - cy)

        # Deterministic tie-breaking: higher score first, then smaller center_dist, then smaller (ny,nx), then stable move preference.
        score = (on_unclaimed * 1000 + on_opp * 700) - dmin - int(center_dist * 2)
        key = (-score, int(center_dist * 10), ny, nx, dy, dx)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1]