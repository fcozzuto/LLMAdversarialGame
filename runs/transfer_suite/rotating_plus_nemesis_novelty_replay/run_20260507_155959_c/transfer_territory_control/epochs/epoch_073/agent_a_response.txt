def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def parse_cells(key):
        s = set()
        for c in observation.get(key) or []:
            if c is not None and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    self_t = parse_cells("self_territory")
    opp_t = parse_cells("opponent_territory")
    unclaimed = parse_cells("unclaimed_cells")

    neigh = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    opp_neighbors = set()
    if opp_t:
        for (x, y) in opp_t:
            for dx, dy in neigh:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    opp_neighbors.add((nx, ny))

    # Precompute closest distances to opponent territory (small fallback if empty).
    opp_list = list(opp_t)
    has_opp = bool(opp_list)
    def min_dist_to_opp(x, y):
        if not has_opp:
            return abs(x - ox) + abs(y - oy)
        md = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < md:
                md = d
        return md

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0

        if (nx, ny) in opp_t:
            score += 7
        if (nx, ny) in unclaimed:
            score += 3
        if (nx, ny) in opp_neighbors:
            score += 2

        # Expansion/pressure: reduce distance to opponent territory or push toward their frontier.
        d = min_dist_to_opp(nx, ny)
        sd = min_dist_to_opp(sx, sy)
        score += (sd - d) * 1.2

        # Avoid drifting into our own dead zone only if it blocks expansion.
        if (nx, ny) in self_t:
            score -= 0.3

        # Prefer safe unclaimed adjacent when possible.
        if opp_t and (nx, ny) in opp_neighbors and (nx, ny) not in self_t:
            score += 0.6

        if score > best_score:
            best_score = score
            best = [dx, dy]

    # If all moves blocked, stay.
    return best if best is not None else [0, 0]