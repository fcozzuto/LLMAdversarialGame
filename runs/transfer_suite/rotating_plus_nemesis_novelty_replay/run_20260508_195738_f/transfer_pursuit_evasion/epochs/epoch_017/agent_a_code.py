def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    is_pursuer = ("purs" in self_role) or ("purs" in opponent_role) or ("evader" not in self_role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def sgn(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    if is_pursuer:
        tx = ox + sgn(ox - sx)
        ty = oy + sgn(oy - sy)
        if not inb(tx, ty):
            tx, ty = ox, oy
        best = None
        best_sc = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            sc = dist2(nx, ny, tx, ty) * 4 + dist2(nx, ny, ox, oy)
            if best_sc is None or sc < best_sc:
                best_sc = sc
                best = [dx, dy]
        return best if best is not None else [0, 0]
    else:
        # Evader: run from predicted pursuer next step (opponent continues away from us)
        tx = ox + sgn(ox - sx)
        ty = oy + sgn(oy - sy)
        if not inb(tx, ty):
            tx, ty = ox, oy
        best = None
        best_sc = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            sc = dist2(nx, ny, tx, ty) * 4 + dist2(nx, ny, ox, oy)
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return best if best is not None else [0, 0]