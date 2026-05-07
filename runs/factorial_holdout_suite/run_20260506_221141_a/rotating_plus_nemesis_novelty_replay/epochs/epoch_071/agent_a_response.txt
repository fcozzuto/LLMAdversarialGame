def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)
    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obs.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs: resources.append((x, y))
    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [int(dx), int(dy)]

    def md(x1, y1, x2, y2):  # L1 distance
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Evaluate the best "advantage" resource after taking one move, with tie-breakers.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine will keep in place on invalid
        val = -10**18
        for tx, ty in resources:
            sd = md(nx, ny, tx, ty)
            od = md(ox, oy, tx, ty)
            # Main: maximize arrival advantage; secondary: ensure closeness; tertiary: avoid walls/obstacles by preferring safer cells.
            adv = od - sd
            clos = -sd
            safe = 0
            for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                px, py = nx + ax, ny + ay
                if inb(px, py) and (px, py) not in obs:
                    safe += 1
            cand = adv * 1000 + clos * 10 + safe
            if cand > val:
                val = cand
        # Deterministic tie-breaker: prefer moves that reduce distance to the currently best resource for us.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # tie-break by minimal self distance to nearest resource
            def nearest_dist(x, y):
                m = 10**9
                for tx, ty in resources:
                    d = md(x, y, tx, ty)
                    if d < m: m = d
                return m
            if nearest_dist(sx + dx, sy + dy) < nearest_dist(sx + best_move[0], sy + best_move[1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]