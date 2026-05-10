def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp = []
    for t in observation.get("opponent_territory") or []:
        if t and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                opp.append((x, y))

    unclaimed = []
    for c in observation.get("unclaimed_cells") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))

    if opp:
        targets = opp
    else:
        targets = unclaimed

    if not targets:
        return [0, 0]

    # Prefer countering toward opponent corner; otherwise nearest target.
    oc = observation.get("opponent_position", [w - 1, h - 1])
    ocx, ocy = int(oc[0]), int(oc[1])

    def score_target(tx, ty):
        md = abs(tx - sx) + abs(ty - sy)
        corner_bias = abs(ocx - tx) + abs(ocy - ty)
        return (md, corner_bias, tx, ty)

    tx, ty = min(targets, key=lambda t: score_target(t[0], t[1]))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (10**9, 10**9, 10**9, 0, 0)

    # Choose neighbor that minimizes distance to target while avoiding obstacles.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        # Slightly prefer moves that also reduce distance to opponent corner.
        corner = abs(ocx - nx) + abs(ocy - ny)
        # Tie-break deterministically toward staying still, then positive directions.
        tie = (0 if (dx == 0 and dy == 0) else 1, dx, dy)
        cand = (nd, corner, tie[0], tie[1], tie[2])
        if cand < best:
            best = (cand[0], cand[1], cand[2], dx, dy)

    if best[3] == 0 and best[4] == 0:
        return [0, 0]

    # If all safe moves were blocked (rare), try staying.
    return [int(best[3]), int(best[4])]