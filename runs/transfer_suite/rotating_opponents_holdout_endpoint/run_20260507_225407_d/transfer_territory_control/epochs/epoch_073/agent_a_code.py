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

    opp = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles and (x, y) not in opp:
                    unclaimed.add((x, y))

    # small determinism boost: prefer moves that increase x then y slightly
    def adj_to_opp(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in opp:
                    c += 1
        return c

    best = None
    best_score = -10**18
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in opp:
            score += 500000  # immediate flip advantage
            score += 50 * adj_to_opp(nx, ny)
        elif (nx, ny) in unclaimed:
            score += 200000
            score += 200 * adj_to_opp(nx, ny)
        else:
            # moving through our area: keep progressing toward fronts
            score += 5 * adj_to_opp(nx, ny)

        # distance-to-center preference to avoid getting stuck in corners
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_now = abs(sx - cx) + abs(sy - cy)
        dist_new = abs(nx - cx) + abs(ny - cy)
        score += int((dist_now - dist_new) * 30)

        # slight tie-break toward increasing x, then y
        score += (nx - sx) * 2 + (ny - sy)

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]