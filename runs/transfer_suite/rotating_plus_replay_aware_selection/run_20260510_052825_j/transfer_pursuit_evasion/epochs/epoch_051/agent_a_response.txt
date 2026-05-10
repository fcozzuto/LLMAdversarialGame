def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def obst_pen(nx, ny):
        if (nx, ny) in obstacles:
            return 10_000
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    p += 3
        return p

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Anticipate zigzag: aim slightly ahead of opponent relative direction to our position.
    vx = 0 if ox == sx else (1 if ox > sx else -1)
    vy = 0 if oy == sy else (1 if oy > sy else -1)
    ahead_x = ox + vx
    ahead_y = oy + vy
    if not inb(ahead_x, ahead_y):
        ahead_x, ahead_y = ox, oy

    best = None
    best_i = 0
    for i, (dx, dy) in enumerate(deltas):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pen = obst_pen(nx, ny)
        if self_is_evader:
            # maximize separation; prefer moving towards farther corners to break zigzags
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_d = max(dist2(nx, ny, cx, cy) for (cx, cy) in corners)
            val = 1.4 * dist2(nx, ny, ox, oy) + 0.9 * dist2(nx, ny, ahead_x, ahead_y) + 0.2 * corner_d - pen
        else:
            # minimize separation; also bias to intercept around ahead position
            val = -1.6 * dist2(nx, ny, ox, oy) - 1.0 * dist2(nx, ny, ahead_x, ahead_y) - 0.15 * (abs(nx - ox) + abs(ny - oy)) - pen

        if best is None or val > best:
            best, best_i = val, i

    dx, dy = deltas[best_i]
    return [dx, dy]