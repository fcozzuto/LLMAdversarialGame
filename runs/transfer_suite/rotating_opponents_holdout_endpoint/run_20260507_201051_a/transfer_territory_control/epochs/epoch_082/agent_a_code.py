def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    un = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                un.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    if not dirs:
        return [0, 0]

    # Prefer moves that head toward nearest unclaimed; break ties deterministically.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue

        if un:
            # minimize distance to nearest unclaimed; then maximize distance from opponent
            dmin = None
            for x, y in un:
                d = abs(x - nx) + abs(y - ny)
                if dmin is None or d < dmin or (d == dmin and (x, y) < best):
                    dmin = d
            score = (0, dmin, -(abs(ox - nx) + abs(oy - ny)))
        else:
            # No unclaimed known: chase opponent (deterministic)
            score = (1, abs(ox - nx) + abs(oy - ny), 0)

        if best is None or score < best[0]:
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]