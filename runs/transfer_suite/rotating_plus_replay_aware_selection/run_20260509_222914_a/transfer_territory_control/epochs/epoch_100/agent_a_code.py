def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed_list = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2]
    unclaimed = set(unclaimed_list)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not self_ter:
        return [0, 0]

    frontier = set()
    if unclaimed:
        for x, y in self_ter:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and (nx, ny) in unclaimed:
                        frontier.add((nx, ny))

    targets = list(frontier) if frontier else unclaimed_list
    if not targets:
        if opp_ter:
            targets = list(opp_ter)
        else:
            return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Precompute nearest distance to any target from current position for shaping
    def nearest_dist(px, py, tlist):
        md = None
        for tx, ty in tlist:
            d = abs(tx - px) + abs(ty - py)
            if md is None or d < md:
                md = d
        return md if md is not None else 0

    best = None
    cur_to_target = nearest_dist(sx, sy, targets)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        in_un = (nx, ny) in unclaimed
        in_frontier = (nx, ny) in frontier
        in_opp = (nx, ny) in opp_ter
        in_self = (nx, ny) in self_ter

        # If we step into unclaimed/our frontier, prioritize strongly; prefer moving closer to some target.
        d_to_target = nearest_dist(nx, ny, targets)

        score = 0
        if in_un:
            score += 120
        if in_frontier:
            score += 60
        if in_opp:
            score += 35
        if in_self:
            score += 10
        # Encourage progress (lower distance is better); also slightly prefer moves that reduce distance more than staying
        delta_prog = (cur_to_target - d_to_target)
        score += 8 * delta_prog
        # Tiny deterministic tie-break to avoid oscillation: prefer larger x then y
        score += 0.001 * (nx * 0.1 + ny)

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]