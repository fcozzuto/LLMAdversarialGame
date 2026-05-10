def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "")
    opp_role = str(observation.get("opponent_role") or "")
    s = (self_role + " " + opp_role).lower()
    pursue = ("pursuer" in self_role.lower()) or ("pursuer" in s and "evader" not in self_role.lower())

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        d = abs(nx - ox) + abs(ny - oy)
        # bonus for steering away/toward with slight tie-break toward center (evader) or away from edges (pursuer)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = abs(nx - cx) + abs(ny - cy)

        # corner pressure: evader prefers larger distance and closer to center; pursuer prefers smaller distance and closer to opponent path
        if pursue:
            score = (-d * 1000) + (-(center_dist * 2))
        else:
            score = (d * 1000) + (-(center_dist * 1.5))

        # avoid getting boxed by obstacles: count free neighbors deterministically
        free = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx, ty = nx + adx, ny + ady
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    free += 1
        score += free if not pursue else (free * 0.25)

        if best_score is None or score > best_score:
            best_score = score
            best = [int(nx - sx), int(ny - sy)]

    return [best[0], best[1]]