def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w)
    except:
        w = 8
    try:
        h = int(h)
    except:
        h = 8

    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_terr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_v = -10**18

    # If there is unclaimed territory, bias towards it; otherwise bias towards opponent / center.
    has_unclaimed = bool(unclaimed)
    center = (w // 2, h // 2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_center = abs(nx - center[0]) + abs(ny - center[1])

        v = 0
        if has_unclaimed:
            if (nx, ny) in unclaimed:
                v += 10000
            elif (nx, ny) in self_terr:
                v -= 20
            elif (nx, ny) in opp_terr:
                v -= 200
            else:
                v -= 5
            # Encourage moves that reduce distance to the closest unclaimed cell.
            # Deterministic: compute a small sample to keep fast.
            closest = 10**9
            for ux, uy in (list(unclaimed)[:30]):
                cd = abs(nx - ux) + abs(ny - uy)
                if cd < closest:
                    closest = cd
            v += max(0, 300 - closest)
        else:
            if (nx, ny) in opp_terr:
                v -= 300
            if (nx, ny) in self_terr:
                v += 10
            v += max(0, 200 - d_opp)
            v += 0.1 * (-d_center)

        if v > best_v:
            best_v = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]