def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        return [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    def man(x, y, tx, ty):
        return abs(tx - x) + abs(ty - y)

    # Prefer edge cells: unclaimed cells adjacent to opponent territory
    edge_targets = []
    if unclaimed and opp_terr:
        for ux, uy in unclaimed:
            for vx, vy in neighbors8(ux, uy):
                if (vx, vy) in opp_terr:
                    edge_targets.append((ux, uy))
                    break

    if edge_targets:
        targets = edge_targets
    elif unclaimed:
        targets = list(unclaimed)
    elif opp_terr:
        targets = list(opp_terr)
    else:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Pick best 1-step move using deterministic heuristic to nearest target,
    # with bonus for stepping into opponent territory (flipping on entry).
    best = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_score = 10**9
        tx = ty = 0
        # evaluate against a small deterministic subset: closest few targets by manhattan
        for i in range(len(targets)):
            if i > 18:
                break
            t = targets[i]
            d = man(nx, ny, t[0], t[1])
            if d < dist_score:
                dist_score = d
                tx, ty = t[0], t[1]
        flip_bonus = -3 if (nx, ny) in opp_terr else 0
        # Encourage advancement direction (toward chosen target)
        adv = -man(nx, ny, tx, ty)
        # Tie-break deterministically by (dx,dy)
        score = dist_score + (-adv) + flip_bonus + (0 if dx == 0 else 0.001 * (dx + 1)) + 0.0001 * (dy + 1)
        cand = (score, dx, dy)
        if cand < best:
            best = cand

    return [int(best[1]), int(best[2])]