def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = abs(ox - nx) + abs(oy - ny)
                if val < best[0]:
                    best = (val, dx, dy)
        return [best[1], best[2]]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a promising resource: where we are closer than opponent, preferring larger lead.
    best_res = None
    best_key = None
    for rx, ry in resources:
        md = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # prefer resources with (od-md) large; then smaller md as tie-break
        key = (-(od - md), md, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    tx, ty = best_res

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        opp_d = (tx - ox) * (tx - ox) + (ty - oy) * (ty - oy)

        # If we step onto/near resources, it should strongly help.
        # Also mildly penalize moves that let opponent be equally close.
        lead_after = (man(ox, oy, tx, ty) - man(nx, ny, tx, ty))

        # Bonus for progressing towards target in manhattan sense
        prog = man(sx, sy, tx, ty) - man(nx, ny, tx, ty)

        # Small tie-breaker: avoid increasing distance to opponent's position too much
        opp_pressure = man(nx, ny, ox, oy)

        val = (my_d, -lead_after, -prog, opp_pressure)
        if val < best_move[0:4]:
            best_move = (val[0], dx, dy)

    return [best_move[1], best_move[2]]