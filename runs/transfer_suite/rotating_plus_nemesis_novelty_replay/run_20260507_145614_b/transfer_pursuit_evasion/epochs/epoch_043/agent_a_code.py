def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))
    evader = bool(evader)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy
    def free_neigh(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    if evader:
        # Flee to farthest reachable cell, tie-break by safety (more free neighbors).
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            s = free_neigh(nx, ny)
            score = (d, s, -nx, -ny)  # deterministic tie-break
            if best is None or score > best[0]:
                best = (score, [dx, dy])
        return best[1] if best is not None else [0, 0]
    else:
        # Pursuer: aim one step beyond opponent along current direction (anti-zigzag).
        adx = 0 if ox == sx else (1 if ox > sx else -1)
        ady = 0 if oy == sy else (1 if oy > sy else -1)
        ax = max(0, min(w - 1, ox + adx))
        ay = max(0, min(h - 1, oy + ady))
        if (ax, ay) in obst:
            ax, ay = ox, oy

        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # Primary: reduce distance to extrapolated aim; Secondary: reduce distance to opponent.
            p1 = dist2(nx, ny, ax, ay)
            p2 = dist2(nx, ny, ox, oy)
            s = free_neigh(nx, ny)
            # Deterministic tie-break prefers higher safety and keeping movement towards aim.
            score = (-p1, -p2, s, dx, dy)
            if best is None or score > best[0]:
                best = (score, [dx, dy])
        return best[1] if best is not None else [0, 0]