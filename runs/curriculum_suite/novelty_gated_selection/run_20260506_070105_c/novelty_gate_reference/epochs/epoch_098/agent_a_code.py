def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If a resource is adjacent, take it immediately.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx != 0 or dy != 0) and in_bounds(nx, ny) and (nx, ny) in resources and (nx, ny) not in obstacles:
                return [dx, dy]
    # Also allow staying if current cell is a resource.
    if (sx, sy) in resources:
        return [0, 0]

    # Greedy one-step: head to nearest resource, but keep distance from opponent and avoid their likely probing direction.
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    opp_dx = 0 if ox == sx else (1 if ox > sx else -1)
    opp_dy = 0 if oy == sy else (1 if oy > sy else -1)
    prefer_away_from_diag = (opp_dx, opp_dy)

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Resource objective
        md = 10**9
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if d < md:
                md = d

        # Opponent objective: maximize distance, but also avoid stepping into their diagonal probe "line".
        od = man(nx, ny, ox, oy)
        # If we move in the same diagonal direction from opponent, penalize.
        step_from_opp = (nx - ox, ny - oy)
        step_dx = 0 if step_from_opp[0] == 0 else (1 if step_from_opp[0] > 0 else -1)
        step_dy = 0 if step_from_opp[1] == 0 else (1 if step_from_opp[1] > 0 else -1)
        diag_same = (step_dx, step_dy) == prefer_away_from_diag  # note: this means aligned with opponent relative direction
        diag_pen = 5 if diag_same else 0

        # Small tie-breaker deterministic: prefer non-zero moves that reduce md; otherwise lexicographic.
        score = (md, -od, diag_pen, abs(dx) + abs(dy), dx, dy)

        if best is None or score < best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]