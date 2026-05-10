def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("hunter" in self_role) or (self_role == "pursuer")
    if not pursuer and opponent_role:
        pursuer = not ("evad" in opponent_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)
        if pursuer:
            # chase while slightly favoring alignment (helps against wall-run patterns)
            align = (abs((nx - sx)) + abs((ny - sy))) + (1 if (dx != 0 and dy != 0) else 0)
            score = dist * 1000 - align
        else:
            # evade while avoiding moves that reduce distance
            align = (abs((nx - sx)) + abs((ny - sy))) + (1 if (dx == 0 or dy == 0) else 0)
            score = -dist * 1000 + align
        if best is None or score < best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        # deterministic fallback: greedy sign step without obstacle checks
        tx = 0 if ox == sx else (1 if ox > sx else -1)
        ty = 0 if oy == sy else (1 if oy > sy else -1)
        if not pursuer:
            tx, ty = -tx, -ty
        nx, ny = sx + tx, sy + ty
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [int(tx), int(ty)]
        return [0, 0]

    return [int(best[0]), int(best[1])]