def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    rseen = set()
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs and (x, y) not in rseen:
                rseen.add((x, y))
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) in rseen:
            return [dx, dy]

        if resources:
            # Prefer moves where we are closer to a resource than the opponent.
            # Deterministic tie-break by closer resource, then lower opponent distance.
            score = 0
            for tx, ty in resources:
                md = dist(nx, ny, tx, ty)
                od = dist(ox, oy, tx, ty)
                if md == 0:
                    score = 10**9
                    break
                # Big bonus for win (closer than opponent), smaller for approaching.
                score = max(score, (od - md) * 100 - md)
            # Add slight preference to reduce opponent advantage globally
            score += -dist(nx, ny, ox, oy)
        else:
            # No visible resources: reduce distance to opponent deterministically.
            score = -dist(nx, ny, ox, oy)

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best