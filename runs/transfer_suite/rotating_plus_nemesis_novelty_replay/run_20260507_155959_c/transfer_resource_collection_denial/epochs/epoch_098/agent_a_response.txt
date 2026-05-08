def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx != 0 or dy != 0) and inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if (sx, sy) not in obs:
        moves.append((0, 0))
    if not moves:
        return [0, 0]

    def cd(x1, y1, x2, y2):  # chebyshev distance with diagonal moves
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        tx = (w - 1) if ox < w // 2 else 0
        ty = (h - 1) if oy < h // 2 else 0
        best = None
        bestd = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = cd(nx, ny, tx, ty)
            key = (d, nx, ny)
            if best is None or key < bestd:
                bestd = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        chosen = None
        chosen_adv = None
        chosen_dist = None
        chosen_tieb = None
        for rx, ry in resources:
            our_d = cd(nx, ny, rx, ry)
            opp_d = cd(ox, oy, rx, ry)
            adv = opp_d - our_d  # positive if we are closer
            tieb = (rx + ry) & 3  # deterministic tiny tie-break
            if (chosen is None or
                adv > chosen_adv or
                (adv == chosen_adv and (our_d < chosen_dist or (our_d == chosen_dist and (tieb, rx, ry) < chosen_tieb)))):
                chosen = (rx, ry)
                chosen_adv = adv
                chosen_dist = our_d
                chosen_tieb = (tieb, rx, ry)

        rx, ry = chosen
        primary = (-chosen_adv, chosen_dist, rx, ry)
        # Small bias to avoid letting opponent take a closer resource next turn (approx.)
        opp_closest = min(cd(ox, oy, r[0], r[1]) for r in resources)
        key = (primary, opp_closest, nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]