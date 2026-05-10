def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    st = int(observation.get("self_territory_count") or 0)
    ot = int(observation.get("opponent_territory_count") or 0)
    we_lead = st >= ot

    resources = observation.get("resources") or []
    unclaimed = observation.get("unclaimed_cells") or []
    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    target = None
    bestd = 10**9

    if resources and int(observation.get("remaining_resource_count") or 0) > 0:
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                tx, ty = int(r[0]), int(r[1])
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    d = man(self_pos, (tx, ty))
                    if d < bestd:
                        bestd, target = d, (tx, ty)
    if target is None and unclaimed:
        if we_lead:
            for c in unclaimed:
                if isinstance(c, (list, tuple)) and len(c) >= 2:
                    tx, ty = int(c[0]), int(c[1])
                    if inb(tx, ty) and (tx, ty) not in obstacles:
                        d = man(self_pos, (tx, ty))
                        if d < bestd:
                            bestd, target = d, (tx, ty)
        else:
            # Try to take cells closer to opponent first
            candidates = []
            for c in unclaimed:
                if isinstance(c, (list, tuple)) and len(c) >= 2:
                    tx, ty = int(c[0]), int(c[1])
                    if inb(tx, ty) and (tx, ty) not in obstacles:
                        d = man(opp_pos, (tx, ty))
                        candidates.append((d, man(self_pos, (tx, ty)), (tx, ty)))
            candidates.sort()
            if candidates:
                target = candidates[0][2]

    if target is None:
        # Fallback: chase/hold depending on lead
        target = (ox, oy) if not we_lead else self_pos

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    bestm = (0, 0)
    bestscore = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to = man((nx, ny), target)
        d_opp = man((nx, ny), opp_pos)
        # Higher is better: closer to target, and if behind, also avoid giving opponent easy access
        score = -d_to
        if we_lead:
            score += 0.2 * d_opp
        else:
            score += -0.1 * d_opp
        if score > bestscore:
            bestscore, bestm = score, [dx, dy]
    return bestm if bestm != (0, 0) or ((