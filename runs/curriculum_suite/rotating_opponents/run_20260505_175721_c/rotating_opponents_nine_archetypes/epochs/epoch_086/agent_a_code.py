def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource we can contest: maximize (opp-self), then closeness.
    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Encourage being strictly faster; if not, still allow if close by absolute distance.
        lead = od - sd
        dist_pen = sd
        score = lead * 10 - dist_pen
        key = (score, -dist_pen, -(abs(tx - sx) + abs(ty - sy)))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                deltas.append((dx, dy))

    # Greedy step minimizing distance to target, with obstacle penalty and small anti-opponent pressure.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        val = cheb(nx, ny, tx, ty)
        if (nx, ny) in obstacles:
            val += 1000
        # If we move closer to opponent while we're behind on target, slightly discourage.
        cur_sd = cheb(sx, sy, tx, ty)
        cur_od = cheb(ox, oy, tx, ty)
        if cur_od > cur_sd:
            val += 0.15 * cheb(nx, ny, ox, oy)
        # Break ties deterministically: prefer diagonal, then right, then up, then still.
        tie = (-(1 if dx != 0 and dy != 0 else 0), -dx, -dy, -1 if (dx == 0 and dy == 0) else 0)
        cur = (val, tie)
        if best_val is None or cur < best_val:
            best_val = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]