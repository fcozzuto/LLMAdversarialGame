def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for a in (observation.get("obstacles") or []):
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))
        elif isinstance(a, dict) and "x" in a and "y" in a:
            obs.add((int(a["x"]), int(a["y"])))

    def parse_xy(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict) and "x" in r and "y" in r:
            return int(r["x"]), int(r["y"])
        return None

    resources = []
    for r in (observation.get("resources") or []):
        p = parse_xy(r)
        if p is not None:
            x, y = p
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_target():
        # Prefer resources we can reach earlier than opponent; if tie, prefer closer.
        best = None
        best_key = None
        for rx, ry in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Also lightly favor central-ish positions to reduce getting stuck.
            cd = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
            key = (od - sd, -sd, -cd)
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        return best

    tx, ty = best_target()

    actions = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                actions.append((dx, dy))
    if not actions:
        return [0, 0]

    best_move = None
    best_score = None
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        sd = dist(nx, ny, tx, ty)
        # Deny: maximize increase in opponent's distance to our target (or decrease if they already closer).
        od = dist(ox, oy, tx, ty)
        # Also discourage moving into positions that are closer to an "opponent-favored" resource.
        deny_pen = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            # If opponent is closer to that resource than we are, being close to it helps them.
            if dist(ox, oy, rx, ry) < dist(nx, ny, rx, ry):
                deny_pen += 0
            else:
                deny_pen += max(0, 3 - dist(nx, ny, rx, ry))
        # Prefer moves that reduce self distance; when tied, prefer higher deny.
        score = (-sd, od - dist(ox, oy, tx, ty), -deny_pen, -abs(nx - tx) - abs(ny - ty))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]