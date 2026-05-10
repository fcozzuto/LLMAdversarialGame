def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    # In pursuit_evasion, pursuer maximizes capture; evader maximizes survival.
    self_is_pursuer = ("pursuer" in self_role) or ("pursuer" in opp_role and "evader" in self_role == False)
    if ("pursuer" not in self_role) and ("evader" not in self_role) and ("pursuer" in opp_role):
        self_is_pursuer = False

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def dist_cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = dist_cheb(nx, ny)

        # Small deterministic lookahead: second step direction to opponent/farthest corner.
        # This helps against direct pursuit without full search.
        best2 = None
        for ddx, ddy in moves:
            x2, y2 = nx + ddx, ny + ddy
            if not ok(x2, y2):
                continue
            dd = dist_cheb(x2, y2)
            val = dd if not self_is_pursuer else dd
            if best2 is None:
                best2 = val
            else:
                if self_is_pursuer:
                    best2 = val if val < best2 else best2
                else:
                    best2 = val if val > best2 else best2
        if best2 is None:
            best2 = d

        if self_is_pursuer:
            # prefer smaller distance; tie-break by moving more toward opponent, then lexicographic
            tie1 = -((1 if nx > sx else 0) * (1 if ox > sx else 0) + (1 if nx < sx else 0) * (1 if ox < sx else 0))
            key = (best2, -abs(nx - sx) - abs(ny - sy), dx, dy, nx, ny)
        else:
            # prefer larger distance; tie-break by moving away from opponent, then lexicographic
            key = (-best2, -abs(nx - sx) - abs(ny - sy), dx, dy, nx, ny)

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]