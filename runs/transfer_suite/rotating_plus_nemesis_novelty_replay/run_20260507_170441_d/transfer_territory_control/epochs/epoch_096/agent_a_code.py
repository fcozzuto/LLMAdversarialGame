def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                targets.append((x, y))
        except:
            pass

    if not targets:
        unclaimed = observation.get("unclaimed_cells") or []
        for c in unclaimed:
            try:
                x, y = int(c[0]), int(c[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                    targets.append((x, y))
            except:
                pass

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_self = abs(nx - sx) + abs(ny - sy)
        if targets:
            dmin = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            score = -dmin * 10 - dist_opp + (-dist_self)
        else:
            score = -dist_opp * 2 - dist_self

        # Deterministic tie-break: prefer smaller dx then dy among same score
        if score > best_score or (score == best_score and (best is None or (dx, dy) < best)):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]