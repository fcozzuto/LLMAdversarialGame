def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Precompute some useful front sets
    un_adj_to_opp = []
    un_adj_to_self = []
    for (ux, uy) in unclaimed:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = ux + dx, uy + dy
                if (nx, ny) in opp_set:
                    un_adj_to_opp.append((ux, uy))
                    dx = dy = 2  # break both-ish
                if (nx, ny) in self_set:
                    un_adj_to_self.append((ux, uy))
        if len(un_adj_to_opp) > 6 and len(un_adj_to_self) > 6:
            break

    opp_pos = observation.get("opponent_position", (7, 7))
    myc = observation.get("self_territory_count", len(self_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    target_bias = 1.6 if opc > myc else 1.0  # if behind, cut opponent more

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**9, 0, 0)
    pref = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    for dx, dy in pref:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        cell = (nx, ny)
        score = 0

        if cell in opp_set:
            score += 1000  # immediate capture
        if cell in self_set:
            score += 5
        if cell in unclaimed:
            score += 50  # expansion

        # Avoid wasting moves into dead areas by steering to strategic frontiers
        if un_adj_to_opp:
            d_oppfront = min(dist((nx, ny), p) for p in un_adj_to_opp)
            score += int(60 * target_bias / (1 + d_oppfront))
        if un_adj_to_self:
            d_selffront = min(dist((nx, ny), p) for p in un_adj_to_self)
            score += int(30 / (1 + d_selffront))

        # Also keep some pressure near opponent
        score += int(20 / (1 + dist((nx, ny), opp_pos)))

        if score > best[0] or (score == best[0] and (dx, dy) == (best[1], best[2])):
            best = (score, dx, dy)

    return [best[1], best[2]]