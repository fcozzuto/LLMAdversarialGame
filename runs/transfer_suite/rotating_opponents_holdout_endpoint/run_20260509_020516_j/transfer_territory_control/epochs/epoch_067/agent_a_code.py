def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    my_t = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                my_t.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                opp_t.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                unclaimed.add((x, y))

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Build "frontier targets": unclaimed cells adjacent to opponent territory
    targets = []
    for (ux, uy) in unclaimed:
        for dx, dy in dirs:
            nx, ny = ux + dx, uy + dy
            if (nx, ny) in opp_t:
                targets.append((ux, uy))
                break
    if not targets:
        targets = list(unclaimed) if unclaimed else [(cx, cy)]

    best = None
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Nearest-target distance (prefer getting closer to frontier)
        md = 10**9
        for tx, ty in targets[:64]:
            d = abs(tx - nx) + abs(ty - ny)
            if d < md:
                md = d

        score = 0
        if (nx, ny) in opp_t:
            score += 40  # direct counterclaim
        elif (nx, ny) in unclaimed:
            score += 18  # expand territory
        elif (nx, ny) in my_t:
            score += 4   # maintain
        else:
            score += 0

        # Encourage moving toward frontier/expansion, and slightly toward center
        score += -2.5 * md
        score += -0.1 * (abs(nx - cx) + abs(ny - cy))

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]