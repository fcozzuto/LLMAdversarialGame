def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocks

    def dist(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    # Target selection: push into/adjacent to opponent territory; else grab nearest unclaimed.
    target = None
    if opp_terr:
        adj_candidates = []
        for (ox, oy) in opp_terr:
            for dx, dy in dirs:
                nx, ny = ox + dx, oy + dy
                if ok(nx, ny) and (nx, ny) not in blocks and ((nx, ny) in unclaimed or (nx, ny) in opp_terr):
                    if (nx, ny) in unclaimed or (nx, ny) in opp_terr:
                        adj_candidates.append((nx, ny))
        if adj_candidates:
            # deterministic min: nearest then lexicographic
            target = min(set(adj_candidates), key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))
        else:
            target = min(opp_terr, key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))
    if target is None:
        if unclaimed:
            target = min(unclaimed, key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))
        else:
            target = min(self_terr or [(sx, sy)], key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))

    # Local move scoring: immediate territory advantage + progress to target.
    best_move = [0, 0]
    best_score = -10**18
    tx, ty = int(target[0]), int(target[1])

    # Extra deterministic bias: prefer moves that approach target (ties broken by dx,dy ordering).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 3
        elif (nx, ny) in opp_terr:
            score += 5  # flipping on entry
        elif (nx, ny) in self_terr:
            score += 1  # maintain control
        # Progress
        score += -dist(nx, ny, tx, ty)
        # Slight penalty for staying still unless no options
        if dx == 0 and dy == 0:
            score -= 0.5
        # Deterministic tie-break: lexicographic by (dx,dy)
        tiebreak = - (dx * 10 + dy)
        score += tiebreak * 1e-3

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # Ensure integers in allowed set
    return [int(best_move[0]), int(best_move[1])]