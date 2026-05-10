def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or (0, 0)
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    opp_terr = observation.get("opponent_territory") or []
    opp_set = set()
    for p in opp_terr:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_set.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    un = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                un.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        # Prefer moves that get closer to unclaimed, but keep some distance from opponent territory.
        if un:
            # nearest unclaimed distance from (nx,ny)
            dmin = 10**9
            for tx, ty in un:
                d = abs(nx - tx) + abs(ny - ty)
                if d < dmin:
                    dmin = d
        else:
            dmin = abs(nx - ox) + abs(ny - oy)
        if opp_set:
            do = 10**9
            for tx, ty in opp_set:
                d = abs(nx - tx) + abs(ny - ty)
                if d < do:
                    do = d
        else:
            do = abs(nx - ox) + abs(ny - oy)
        # Also softly avoid stepping directly onto opponent territory cells when possible.
        on_opp = 1 if (nx, ny) in opp_set else 0
        # Deterministic tie-breakers: prefer lexicographically smaller (dx,dy) after score.
        score = (-dmin) + 0.25 * do - 2.0 * on_opp
        cand.append((score, abs(dx) + abs(dy), dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    best = cand[0]
    return [int(best[2]), int(best[3])]