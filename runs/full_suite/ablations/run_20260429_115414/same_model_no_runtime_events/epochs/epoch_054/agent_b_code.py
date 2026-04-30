def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_step(tx, ty, prefer_away_from_opp):
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if not valid(nx, ny):
                    continue
                ds = cheb(nx, ny, tx, ty)
                dso = cheb(nx, ny, ox, oy)
                score = ds * 10 + (0 if prefer_away_from_opp else -dso)
                if prefer_away_from_opp:
                    score = ds * 10 - dso
                if best is None or score < best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                    best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem or 0)
    except:
        rem = 0
    late = rem <= 4

    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prioritize targets where we can arrive earlier; otherwise choose to deny.
            # late-game: prioritize biggest lead; otherwise use a balance.
            lead = do - ds
            key = (-lead if late else (-(lead + 1) if lead > 0 else lead), ds, cheb(rx, ry, 0, 0) + cheb(rx, ry, w - 1, h - 1))
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
        # If opponent is closer to the target, try to move in a way that increases their distance.
        prefer_away = cheb(ox, oy, tx, ty) <= cheb(sx, sy, tx, ty)
        mv = best_step(tx, ty, prefer_away)
        return [int(mv[0]), int(mv[1])]
    else:
        # No visible resources: deterministically drift toward the mid while avoiding opponent.
        target = (w // 2, h // 2) if (sx + sy) % 2 == 0 else (w // 2 - 1 if w > 1 else 0, h // 2)
        prefer_away = True
        mv = best_step(target[0], target[1], prefer_away)
        if mv == [0, 0]:
            # If stuck, stay (engine will keep us anyway).
            return [0, 0]
        return [int(mv[0]), int(mv[1])]