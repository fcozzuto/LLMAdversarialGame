def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    midx, midy = (w - 1) / 2.0, (h - 1) / 2.0
    cx, cy = float(sx), float(sy)

    up = int(observation.get("self_territory_count") or 0)
    opcnt = int(observation.get("opponent_territory_count") or 0)
    we_lead = up >= opcnt

    # Prefer directions that expand territory and/or contest opponent territory, while drifting toward the center.
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        dest = (nx, ny)
        score = 0

        if dest in self_terr:
            score += 1
        elif dest in unclaimed:
            score += 2
        elif dest in op_terr:
            # flipping enabled on entry
            score += 3
            if not we_lead:
                score += 1
        else:
            score += 0

        # center drift (stronger when behind to reduce being boxed in by center-claim)
        dist_center = abs(nx - midx) + abs(ny - midy)
        score += (-0.35 * dist_center)
        if not we_lead:
            score += (-0.15 * dist_center)

        # small anti-stall: slightly prefer moves that reduce manhattan distance to closest unclaimed
        if unclaimed:
            # deterministic: sample few candidates near; avoid heavy computation
            best_d = 10**9
            # simple limited scan over unclaimed sorted by coords
            for i, (ux, uy) in enumerate(sorted(unclaimed)[:64]):
                d = abs(ux - nx) + abs(uy - ny)
                if d < best_d:
                    best_d = d
                if best_d == 0:
                    break
            score += (-0.05 * best_d)

        # tie-break deterministically by preferring earlier directions then less dx, then less dy
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    # If every direction was blocked (unlikely), stay still
    return best_move