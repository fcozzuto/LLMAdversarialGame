def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Target: farthest unclaimed from opponent to avoid feeding center control
    target = None
    best = -1
    for (x, y) in unclaimed:
        if (x, y) in obstacles:
            continue
        d = dist2(x, y, ox, oy)
        if d > best:
            best, target = d, (x, y)
    if target is None:
        # Fallback: opposite-corner from opponent
        target = (0, 0) if dist2(0, 0, ox, oy) >= dist2(w - 1, h - 1, ox, oy) else (w - 1, h - 1)

    tx, ty = target

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_to_t = dist2(nx, ny, tx, ty)
        d_from_opp = dist2(nx, ny, ox, oy)
        in_opp = (nx, ny) in opp_t
        in_self = (nx, ny) in self_t

        # Score: get closer to target, keep away from opponent center; discourage stepping into opp unless it's useful
        score = (-d_to_t) + 0.15 * d_from_opp
        if in_opp:
            # Flipping gives control, but entering opp territory often means contesting their frontier.
            score += 2.5
        if in_self:
            score += 0.5

        # Small tie-breaker: deterministic preference order by dx,dy
        score += 1e-6 * (-(abs(dx) + abs(dy)) + (dx + dy) * 0.01)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]