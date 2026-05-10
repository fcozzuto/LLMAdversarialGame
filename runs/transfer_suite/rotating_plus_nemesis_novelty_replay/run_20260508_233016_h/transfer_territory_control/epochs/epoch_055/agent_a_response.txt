def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    unclaimed = observation.get("unclaimed_cells") or []
    if not unclaimed:
        unclaimed = observation.get("resources") or []
    targets = []
    if unclaimed:
        targets.extend([tuple(p) for p in unclaimed[:40]])
    else:
        targets.extend([tuple(p) for p in opp_set][:20])
    if len(targets) < 40 and opp_set:
        for p in list(opp_set)[:40]:
            if p not in targets:
                targets.append(p)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    nbrs4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell_bonus = 0
        if (nx, ny) in opp_set:
            cell_bonus = 650  # prefer flipping opponent territory
        elif (nx, ny) in self_set:
            cell_bonus = 40
        else:
            cell_bonus = 150  # take unclaimed

        # Prefer moves adjacent to our territory to expand safely
        adj_self = 0
        for ddx, ddy in nbrs4:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in self_set:
                adj_self += 1
        adj_bonus = adj_self * 30

        # Also bias toward the frontier/targets
        dt = 10**9
        for tx, ty in targets[:30]:
            d = man(nx, ny, tx, ty)
            if d < dt:
                dt = d

        do = man(nx, ny, ox, oy)
        score = cell_bonus + adj_bonus - dt * 22 - do * 4

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]