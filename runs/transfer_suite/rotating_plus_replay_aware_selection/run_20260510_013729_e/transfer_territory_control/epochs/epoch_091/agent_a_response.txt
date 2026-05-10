def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    self_set = set()
    opp_set = set()
    for p in self_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs:
                self_set.add((x, y))
    for p in opp_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs:
                opp_set.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    candidates = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                candidates.append((x, y))

    if not candidates:
        # fallback: try to move toward nearest opponent territory cell
        if not opp_set:
            return [0, 0]
        tx, ty = min(opp_set, key=lambda q: abs(q[0] - sx) + abs(q[1] - sy))
    else:
        def adj_to_set(cell, st):
            x, y = cell
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in st:
                        return True
            return False

        # choose best target deterministically
        best = None
        best_score = -10**18
        for x, y in candidates:
            d = max(abs(x - sx), abs(y - sy))
            frontier = 1 if adj_to_set((x, y), self_set) else 0
            threatens = 1 if adj_to_set((x, y), opp_set) else 0
            # Prefer quick expansion along own frontier; if none, contest near opponent.
            score = (10 * frontier) - (2 * d) + (3 * threatens) - (0.2 * (abs(x - sx) + abs(y - sy)))
            # deterministic tie-breaker: smaller x,y
            if score > best_score or (score == best_score and (best is None or (x, y) < best)):
                best_score = score
                best = (x, y)
        tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if not inb(nx, ny) or (nx, ny) in obs:
        # try axis-aligned alternative deterministically
        opts = [(dx, 0), (0, dy), (dx, dy), (0, 0)]
        for odx, ody in opts:
            nx, ny = sx + odx, sy + ody
            if inb(nx, ny) and (nx, ny) not in obs:
                return [int(odx), int(ody)]
        return [0, 0]
    return [int(dx), int(dy)]