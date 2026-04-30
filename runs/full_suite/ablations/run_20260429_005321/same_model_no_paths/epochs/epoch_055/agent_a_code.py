def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    # Score each resource by self advantage: (self_dist - opp_dist), lower is better.
    best_score = None
    best_target = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach at least as fast; tie-break by closer to self, then coords.
        adv = sd - od
        primary = (0 if adv <= 0 else 1, adv, sd, rx, ry)
        if best_score is None or primary < best_score:
            best_score = primary
            best_target = (rx, ry)

    tx, ty = best_target

    # Greedy step towards target with deterministic tie-breaking; if all bad, choose safest alternative towards any resource.
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Also incorporate opponent threat: prefer staying away from opponent slightly.
        threat = cheb(nx, ny, ox, oy)
        # Lower better: first reduce distance to target, then prefer larger threat (i.e., safer)
        candidates.append((d, -threat, dx, dy))
    if candidates:
        candidates.sort()
        _, _, dx, dy = candidates[0]
        return [int(dx), int(dy)]

    # Fallback: pick any valid move that maximizes distance from opponent.
    fallback = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        th = cheb(nx, ny, ox, oy)
        key = (-th, dx, dy)
        if fallback is None or key < fallback[0]:
            fallback = (key, dx, dy)
    if fallback:
        _, dx, dy = fallback
        return [int(dx), int(dy)]

    return [0, 0]