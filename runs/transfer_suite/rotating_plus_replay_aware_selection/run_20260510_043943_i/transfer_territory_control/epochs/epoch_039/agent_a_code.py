def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    unclaimed_set = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))
                unclaimed_set.add((x, y))

    opp_terr_set = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr_set.add((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)

    if unclaimed:
        # Precompute a few target extremes to avoid scanning every time
        # (still deterministic and bounded).
        targets = unclaimed
        if len(targets) > 20:
            targets = sorted(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))[:20]
    else:
        targets = []

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed_set:
            score += 120
        if (nx, ny) in opp_terr_set:
            score += 35  # flipping on entry favors counterclaim

        if targets:
            mind = 10**9
            for tx, ty in targets:
                d = cheb(nx, ny, tx, ty)
                if d < mind:
                    mind = d
            score += 40 / (1 + mind)
        else:
            # No unclaimed: push toward opponent territory or their position
            score += 20 / (1 + cheb(nx, ny, ox, oy))
            if opp_terr_set:
                mind = 10**9
                for tx, ty in list(opp_terr_set)[:25]:
                    d = cheb(nx, ny, tx, ty)
                    if d < mind:
                        mind = d
                score += 30 / (1 + mind)

        # Small bias toward staying slightly active: prefer moves that reduce distance to best target
        score += -0.5 * cheb(nx, ny, ox, oy)

        # Deterministic tie-break: fixed order by score then (dx,dy)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]