def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        pts = observation.get(key) or []
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Target: nearest unclaimed that is adjacent to opponent territory; else nearest unclaimed; else nearest opponent territory.
    frontier = set()
    if opp_terr:
        for (x, y) in opp_terr:
            for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
    if frontier:
        targets = list(frontier)
    elif unclaimed:
        targets = list(unclaimed)
    elif opp_terr:
        targets = list(opp_terr)
    else:
        targets = [(ox, oy)]

    # Determine whether we should push (if behind) or lock (if ahead): use territory counts.
    self_cnt = int(observation.get("self_territory_count", len(self_terr)) or 0)
    opp_cnt = int(observation.get("opponent_territory_count", len(opp_terr)) or 0)
    behind = self_cnt <= opp_cnt

    # Bias: favor moving closer to the chosen target, and prefer entering opponent territory/unclaimed.
    def nearest_target_dist(nx, ny):
        bestd = 10**9
        for tx, ty in targets:
            d = abs(nx - tx) + abs(ny - ty)
            if d < bestd:
                bestd = d
        return bestd if bestd != 10**9 else 0

    best_move = (0, 0)
    best_score = -10**18
    # Deterministic tie-break: fixed move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0

        if (nx, ny) in opp_terr:
            score += 18 if behind else 24
        elif (nx, ny) in unclaimed:
            score += 10 if behind else 13
        elif (nx, ny) in self_terr:
            score += 1

        if (nx, ny) in resources:
            score += 9

        # Avoid walking directly away from useful front if possible.
        score += -nearest_target_dist(nx, ny) * (2 if behind else 3)

        # If ahead, slightly prefer keeping distance from opponent to prevent flips.
        # If behind, slight preference to approach opponent.
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        score += (-(d_to_opp)) if behind else (-0.7 * d_to_opp)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]