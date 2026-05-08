def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    self_ter = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_ter = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    # Target: nearest unclaimed on our outer direction away from opponent; fallback to maximize distance.
    tx = 0 if ox > (w - 1) / 2 else (w - 1)
    ty = 0 if oy > (h - 1) / 2 else (h - 1)

    frontier = []
    for (x, y) in unclaimed:
        if x in (0, w - 1) or y in (0, h - 1):
            continue
        # consider cells somewhat aligned with escaping from opponent
        if (x - sx) * (tx - sx) >= 0 and (y - sy) * (ty - sy) >= 0:
            frontier.append((x, y))
    if not frontier:
        frontier = list(unclaimed)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dxdy = (0, 0)
    best_score = None

    # Deterministic move scoring
    # Prefer: moving into unclaimed to grow; prefer crossing/edge toward our direction; avoid obstacles and opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in unclaimed:
            base += 30
        elif (nx, ny) in opp_ter:
            base += 18  # entering flips on entry
        elif (nx, ny) in self_ter:
            base += 6

        # distance to our escape corner (smaller is better)
        base += -3 * man(nx, ny, tx, ty)

        # avoid opponent proximity (larger is better)
        base += 2 * man(nx, ny, ox, oy)

        # discourage stepping next to obstacles if that blocks progress
        adj_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if (ax, ay) in obstacles:
                    adj_obs += 1
        base -= 2 * adj_obs

        # If there is a relevant target, add incentive to reduce distance to it.
        if frontier:
            # deterministic "nearest" via lexicographic tiebreak
            best_t = None
            best_d = None
            for (x, y) in frontier:
                d = man(nx, ny, x, y)
                if best_d is None or d < best_d or (d == best_d and (x, y) < best_t):
                    best_d = d
                    best_t = (x, y)
            base += -5 * best_d

        if best_score is None or base > best_score or (base == best_score and (dx, dy) < best_dxdy):
            best_score = base
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]