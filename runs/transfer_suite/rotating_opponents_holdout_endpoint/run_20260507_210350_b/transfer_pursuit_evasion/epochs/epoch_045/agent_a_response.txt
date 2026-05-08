def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = (observation.get("self_role", "") or "").lower()

    is_evader = ("evader" in self_role) or ("escape" in self_role) or ("flee" in self_role) or ("runner" in self_role)
    is_pursuer = not is_evader

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1); dy = abs(y2 - y1)
        return dx if dx > dy else dy

    # Simple obstacle risk: penalize moves adjacent to obstacles (helps sliding around walls)
    def risk(x, y):
        r = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    r += 1
        return r

    best = None
    best_val = None
    # Deterministic look-ahead: assume opponent moves 1 step in same direction (toward pursuer / away from evader)
    dx_dir = 0 if ox == sx else (1 if ox > sx else -1)
    dy_dir = 0 if oy == sy else (1 if oy > sy else -1)
    o1x = ox - dx_dir if is_evader else ox + dx_dir
    o1y = oy - dy_dir if is_evader else oy + dy_dir
    if not inb(o1x, o1y):
        o1x, o1y = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if is_pursuer:
            # Maximize capture pressure: minimize distance to predicted opponent position
            val = cheb(nx, ny, o1x, o1y) * 100 + risk(nx, ny)
        else:
            # Evader: maximize distance from predicted pursuer position
            val = -cheb(nx, ny, o1x, o1y) * 100 - risk(nx, ny)
            # Extra bias: don't drift into dead corners when already cornered
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]