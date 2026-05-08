def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = dirs[:-1]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def sign(a): return 0 if a == 0 else (1 if a > 0 else -1)

    def adj_unclaimed_count(x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def adj_opp_count(x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_terr:
                c += 1
        return c

    candidates = []
    # Primary: move to best adjacent unclaimed cell that grows our frontier.
    for dx, dy in neigh8:
        tx, ty = sx + dx, sy + dy
        if not inb(tx, ty) or (tx, ty) in obstacles:
            continue
        if (tx, ty) in unclaimed or (tx, ty) in self_terr or (tx, ty) in opp_terr:
            growth = adj_unclaimed_count(tx, ty)
            contest = adj_opp_count(tx, ty)
            dist_opp = abs(tx - ox) + abs(ty - oy)
            to_self = 0 if (tx, ty) in self_terr else 1
            score = growth * 6 + contest * 8 - dist_opp * 0.25 - to_self * 0.1
            candidates.append((score, tx, ty))

    # Secondary: if no useful candidate, step toward opponent's nearest frontier/unclaimed.
    if not candidates:
        best = (-10**18, sx, sy)
        for dx, dy in neigh8:
            tx, ty = sx + dx, sy + dy
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            d = min((abs(ux - tx) + abs(uy - ty)) for ux, uy in unclaimed) if unclaimed else 999
            score = -d
            if score > best[0]:
                best = (score, tx, ty)
        tx, ty = best[1], best[2]
    else:
        _, tx, ty = max(candidates, key=lambda t: (t[0], -(abs(t[1] - ox) + abs(t[2] - oy))))
        # If standing still is best, allow it; else ensure move is legal direction.
        if (tx, ty) == (sx, sy):
            return [0, 0]

    dx = sign(tx - sx)
    dy = sign(ty - sy)
    nx, ny = sx + dx, sy + dy
    if not inb(nx, ny) or (nx, ny) in obstacles:
        return [0, 0]
    return [dx, dy]