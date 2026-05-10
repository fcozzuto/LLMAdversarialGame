def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(nx, ny):
        if nx < 0:
            nx = 0
        elif nx >= w:
            nx = w - 1
        if ny < 0:
            ny = 0
        elif ny >= h:
            ny = h - 1
        return nx, ny

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    near_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def min_obst_dist(nx, ny):
        md = 10**9
        for (x, y) in obstacles:
            d = abs(nx - x) + abs(ny - y)
            if d < md:
                md = d
                if md == 0:
                    break
        return md if md != 10**9 else 99

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            # Deterministic avoidance; engine would keep still if invalid, but score must not prefer it.
            val = -10**12 if pursuer else -10**12
        else:
            d = abs(nx - ox) + abs(ny - oy)
            obst = min_obst_dist(nx, ny)
            center_bias = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * (0.02)
            if pursuer:
                # Chase while avoiding obstacles and slightly biasing toward reducing distance to opponent.
                # Stronger weight for direct pursuit.
                val = (-d) * 10.0 + obst * 0.5 + center_bias
            else:
                # Evade: prioritize moving toward far corner, but only via increasing opponent distance first.
                dc = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
                da = abs(nx - near_corner[0]) + abs(ny - near_corner[1])
                val = d * 10.0 + (-dc) * 0.8 + da * 0.1 + obst * 0.4 + center_bias
        key = (val, -abs(dx), -abs(dy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best