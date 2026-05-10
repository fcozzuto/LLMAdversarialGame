def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return None
        best = None
        best_key = None
        for x, y in resources:
            sd = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            # Prefer resources we can beat (lower sd and larger (od-sd)), then overall closeness.
            # Secondary bias: if close race, choose resource more central (reduces path blocking impact).
            central = -(abs(x - (w - 1) / 2.0) + abs(y - (h - 1) / 2.0))
            key = (od - sd, -sd, central, -x, -y)
            if best_key is None or key > best_key:
                best_key = key
                best = (x, y)
        return best

    tgt = best_target()
    if tgt is None:
        tx, ty = ox, oy
    else:
        tx, ty = tgt

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal step is blocked/outside, try axis-aligned alternatives deterministically.
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    nx, ny = sx + dx, sy + dy
    if ok(nx, ny):
        return [dx, dy]
    nx, ny = sx + dx, sy
    if ok(nx, ny):
        return [dx, 0]
    nx, ny = sx, sy + dy
    if ok(nx, ny):
        return [0, dy]
    # Deterministic fallback: try one of the other diagonal directions that is valid.
    for ddx, ddy in ((1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)):
        nnx, nny = sx + ddx, sy + ddy
        if ok(nnx, nny):
            return [ddx, ddy]
    return [0, 0]