def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for t in (observation.get("obstacles") or []):
        obstacles.add((int(t[0]), int(t[1])))

    selfT = set()
    for t in (observation.get("self_territory") or []):
        selfT.add((int(t[0]), int(t[1])))

    oppT = set()
    for t in (observation.get("opponent_territory") or []):
        oppT.add((int(t[0]), int(t[1])))

    unclaimed = set()
    for t in (observation.get("unclaimed_cells") or []):
        unclaimed.add((int(t[0]), int(t[1])))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**9, 10**9, 0, 0)
    # Heuristic knobs
    INF = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        immediate = 0
        if (nx, ny) in oppT:
            immediate += 6
        elif (nx, ny) in selfT:
            immediate += 2
        elif (nx, ny) in unclaimed:
            immediate += 4
        else:
            immediate += 0

        # Distance to nearest unclaimed cell (encourage expansion)
        d_un = INF
        if unclaimed:
            for ux, uy in unclaimed:
                dd = abs(ux - nx) + abs(uy - ny)
                if dd < d_un:
                    d_un = dd

        # Distance to center (avoid getting stuck in corners)
        d_center = abs(nx - cx) + abs(ny - cy)

        # Slightly prefer moving (unless equally good)
        moved = 0 if (dx == 0 and dy == 0) else 1

        # Tie-break deterministically by position ordering
        # score: maximize immediate, then minimize d_un, then minimize d_center, then prefer move, then lex
        score = immediate * 1000 - (0 if d_un == INF else d_un) * 3 - d_center
        lex = nx * 10 + ny
        cand = (immediate, score, d_un if d_un != INF else 999, d_center, -moved, lex)
        if cand[1] > best[1] or (cand[1] == best[1] and cand[2:] < best[2:]):
            best = (dx, dy), cand[1], cand[2], cand[3], cand[4], cand[5]

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]