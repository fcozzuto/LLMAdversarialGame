def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    self_terr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_terr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    nbrs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = w // 2, h // 2
    edge_bias = 0.0
    if sy in (0, h - 1) or sx in (0, w - 1):
        edge_bias = 0.2

    # Prefer deterministic exploration: boundary/expansion first, then contest, then go center.
    cand_deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**9

    def neighbor_self_count(x, y):
        c = 0
        for dx, dy in nbrs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in self_terr:
                c += 1
        return c

    for dx, dy in cand_deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 40
        if (nx, ny) in opp_terr:
            val += 30
        if (nx, ny) in self_terr:
            val += 10

        # Expansion: prefer moving to cells adjacent to our territory.
        val += 5 * neighbor_self_count(nx, ny)

        # Contest: if we are not expanding, lean toward opponent boundary cells/unclaimed near opponent.
        if not self_terr:
            val += -abs(nx - cx) - abs(ny - cy)
        else:
            if unclaimed:
                # Small tie-break: prefer proximity to the nearest "interesting" unclaimed (adjacent to our territory if possible).
                # Deterministic approximation: use best of a few candidates from the set filtered by adjacency.
                pass

        # Global positioning: softly prefer center to keep options.
        val += edge_bias * (1 if (nx in (0, w - 1) or ny in (0, h - 1)) else 0)
        val += -0.2 * (abs(nx - cx) + abs(ny - cy))

        # Avoid stepping into likely "trap": moving onto opponent territory that is surrounded by opponent more than by self.
        if (nx, ny) in opp_terr:
            opp_adj = 0
            for px, py in nbrs:
                ax, ay = nx + px, ny + py
                if inb(ax, ay) and (ax, ay) in opp_terr:
                    opp_adj += 1
            if opp_adj > 5:
                val -= 8

        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best