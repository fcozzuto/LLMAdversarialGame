def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    if "evader" in self_role:
        self_is_pursuer = False
    elif "pursuer" in self_role:
        self_is_pursuer = True
    else:
        # fallback: if opponent is pursuer, we are evader; otherwise assume pursuer
        self_is_pursuer = ("pursuer" in opp_role) and ("evader" in self_role) == False
        if "pursuer" not in opp_role and "evader" in opp_role:
            self_is_pursuer = False

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    if self_is_pursuer:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dist = cheb(nx, ny)
            # capture if exact
            if dist == 0:
                return [dx, dy]
            # tie-break: prefer moving to reduce distance, then avoid "sticking" (more free neighbors)
            free_n = 0
            for adx, ady in moves:
                tx, ty = nx + adx, ny + ady
                if ok(tx, ty):
                    free_n += 1
            key = (dist, -free_n, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move
    else:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dist = cheb(nx, ny)
            # avoid capture if opponent could match; heuristic: maximize distance now
            free_n = 0
            for adx, ady in moves:
                tx, ty = nx + adx, ny + ady
                if ok(tx, ty):
                    free_n += 1
            key = (-dist, -free_n, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move