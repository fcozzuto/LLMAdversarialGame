def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def neigh_adj(cell, terrset):
        x, y = cell
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in terrset:
                return True
        return False

    chasing = (observation.get("self_territory_count", len(self_terr)) <= observation.get("opponent_territory_count", len(opp_terr)))
    target = None

    if chasing and opp_terr:
        # Counterclaim: move toward the closest opponent-owned cell
        best = None
        bestv = 10**9
        for ox, oy in opp_terr:
            vv = d(sx, sy, ox, oy)
            if vv < bestv or (vv == bestv and (ox, oy) < best):
                bestv = vv
                best = (ox, oy)
        target = best
    else:
        # Secure: unclaimed cells near opponent territory; else near ours; else nearest unclaimed
        candidates = [c for c in unclaimed if neigh_adj(c, opp_terr)] if unclaimed else []
        if not candidates and unclaimed:
            candidates = [c for c in unclaimed if neigh_adj(c, self_terr)] if self_terr else []
        if not candidates:
            candidates = list(unclaimed)
        if candidates:
            target = min(candidates, key=lambda c: (d(sx, sy, c[0], c[1]), c[1], c[0]))

    if target is None:
        return [0, 0]

    tx, ty = target
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Score move by progress to target, plus opportunistic capture
        score = -d(nx, ny, tx, ty)
        if (nx, ny) in opp_terr:
            score += 5 if not chasing else 8
        if (nx, ny) in unclaimed:
            score += 2
        # Prefer expanding our territory (stay away from obstacles already handled) and reduce distance ties deterministically
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]