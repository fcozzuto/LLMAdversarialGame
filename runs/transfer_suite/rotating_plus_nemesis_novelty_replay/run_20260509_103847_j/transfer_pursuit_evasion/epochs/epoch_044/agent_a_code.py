def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda m: (abs(m[0]) + abs(m[1]), m[0], m[1]))  # deterministic tie-break

    def sqdist(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Pick an escape corner deterministically: farthest from opponent.
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    esc = max(corners, key=lambda c: (sqdist(c[0], c[1], ox, oy), -c[0], -c[1]))

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    best = None
    best_val = None
    for dx, dy, nx, ny in candidates:
        # Opponent response: greedy pursuit (minimize distance to us), tie-break deterministically.
        best_od = None
        best_oxn = None
        for odx, ody in moves:
            tx, ty = ox + odx, oy + ody
            if not inside(tx, ty):
                continue
            d = sqdist(tx, ty, nx, ny)
            if best_od is None or d < best_od or (d == best_od and (odx, ody) < best_oxn):
                best_od = d
                best_oxn = (odx, ody)
        odx, ody = best_oxn if best_oxn is not None else (0, 0)
        tox, toy = ox + odx, oy + ody

        # Avoid immediate capture (radius 0 means same cell).
        capture = (tox == nx and toy == ny)

        # Score: maximize distance after response; small bias toward escape corner.
        val = -1 if capture else best_od
        if val != -1:
            val = val * 100 + (-abs(esc[0] - nx) - abs(esc[1] - ny))

        key = (val, -abs(dx) - abs(dy), dx, dy)
        if best is None or key > best_val:
            best_val = key
            best = (dx, dy)
    return [best[0], best[1]]