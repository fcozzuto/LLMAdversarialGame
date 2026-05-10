def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    obs = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs) if isinstance(obs, list) else set()
    self_role = (observation.get("self_role") or "").lower()
    chase = any(k in self_role for k in ("purs", "chase", "tag", "hunter", "pursuer"))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny)
        if chase:
            val = (d, abs(dx) + abs(dy))
        else:
            val = (-d, -(abs(dx) + abs(dy)))
        if best is None or val < best_val:
            best_val = val
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]