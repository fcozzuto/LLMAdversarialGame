def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "pursuer")).lower()
    evading = ("evader" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def corner_score(x, y, want_far):
        # Chebyshev distance to the best corner
        best = -1
        for cx, cy in corners:
            d = max(abs(x - cx), abs(y - cy))
            if d > best:
                best = d
        return best if want_far else -best

    best_move = (0, 0)
    if evading:
        want_far = True
        primary_better = lambda a, b: a > b
    else:
        want_far = False
        primary_better = lambda a, b: a < b

    best_primary = None
    best_secondary = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        dist = max(abs(nx - ox), abs(ny - oy))  # diagonal-friendly
        primary = dist if evading else dist  # same metric; compare direction via primary_better
        secondary = corner_score(nx, ny, want_far)
        if best_primary is None or primary_better(primary, best_primary) or (primary == best_primary and secondary == (best_secondary if best_secondary is not None else secondary) and (dx, dy) < best_move):
            best_primary = primary
            best_secondary = secondary
            best_move = (dx, dy)
        elif primary == best_primary:
            if evading:
                if secondary > best_secondary:
                    best_secondary = secondary
                    best_move = (dx, dy)
            else:
                if secondary > best_secondary:  # remember corner_score returns -best for pursuer; larger is better
                    best_secondary = secondary
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]