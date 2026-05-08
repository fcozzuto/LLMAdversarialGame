def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Choose resource we can reach earlier than opponent; bias toward being closer if tie.
    best = None
    best_score = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        score = (od - sd) * 1000 - sd * 3 - abs(ry - oy)  # deterministic tie-breaking via score
        if best is None or score > best_score or (score == best_score and (rx < best[0] or (rx == best[0] and ry < best[1]))):
            best = (rx, ry)
            best_score = score

    rx, ry = best
    tx = rx - sx
    ty = ry - sy

    def clamp(v):
        if v > 0:
            return 1
        if v < 0:
            return -1
        return 0

    pref = (clamp(tx), clamp(ty))

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cx, cy = sx, sy
    candidates = []
    # First try preferred direction, then fallbacks in fixed order.
    candidates.append(pref)
    px, py = pref
    # If preferred is diagonal, also try straight alternatives.
    candidates.append((px, 0))
    candidates.append((0, py))
    # Then small lexicographic sweep excluding duplicates.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if (dx, dy) != (0, 0) and (dx, dy) != pref:
                candidates.append((dx, dy))
    candidates.append((0, 0))

    seen = set()
    for dx, dy in candidates:
        if (dx, dy) in seen:
            continue
        seen.add((dx, dy))
        nx, ny = cx + dx, cy + dy
        if ok(nx, ny):
            return [int(dx), int(dy)]

    return [0, 0]