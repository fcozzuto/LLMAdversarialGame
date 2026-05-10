def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    oppx, oppy = observation["opponent_position"]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def edge_score(x, y):
        return (x == 0 or x == w - 1) + (y == 0 or y == h - 1)

    # Find best target unclaimed cell based on distance and whether it's adjacent to our territory
    best_t = None
    best_rank = -10**9
    for ux, uy in unclaimed:
        d = man(sx, sy, ux, uy)
        adj = 0
        # 8-neighborhood adjacency to our territory encourages expansion lines
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                if (ux + dx, uy + dy) in self_terr:
                    adj = 1
        rank = (-d) * 2 + adj * 6 + edge_score(ux, uy) * 1
        if rank > best_rank:
            best_rank = rank
            best_t = (ux, uy)

    # If no unclaimed, push toward breaking/pressuring opponent by approaching their territory boundary
    target = best_t
    if target is None:
        best_rank = -10**9
        for ox, oy in opp_terr:
            d = man(sx, sy, ox, oy)
            # closer to opponent territory is better when nothing else exists
            rank = -d + (-man(ox, oy, oppx, oppy))
            if rank > best_rank:
                best_rank = rank
                target = (ox, oy)

    tx, ty = (target if target is not None else (sx, sy))
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        val = 0.0
        # Prefer capturing/holding
        if cell in self_terr: val += 0.5
        if cell in unclaimed: val += 4.0
        if cell in opp_terr:
            # Flipping on entry is allowed: do it if it's near our frontier/goal, but don't wander into deep counterclaim zones
            val += 2.2
            val -= 0.6 * man(nx, ny, oppx, oppy)

        # Advance toward chosen target
        val += 1.8 * (man(sx, sy, tx, ty) - man(nx, ny, tx, ty))

        # Mild edge pressure
        val += 0.2 * edge_score(nx, ny)

        # Avoid getting stuck in our own territory if it means moving away from targets
        if cell not in unclaimed and cell not in opp_terr and cell not in self_terr:
            val -= 0.2

        # Deterministic tie-breaker: prefer lower (dx,dy) lexicographic after value
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move