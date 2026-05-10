def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role and "evad" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target_corner = max(corners, key=lambda c: md(c[0], c[1], sx, sy))  # evasion_corner style
    if self_is_pursuer:
        # Score: go toward target corner AND reduce distance to opponent; avoid obstacles.
        def score(nx, ny):
            d_opp = md(nx, ny, ox, oy)
            d_corner = md(nx, ny, target_corner[0], target_corner[1])
            obst = 1 if (nx, ny) in obstacles else 0
            return (d_opp * 10 + d_corner) + obst * 1000
        best = (10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h): 
                    continue
                if (nx, ny) in obstacles:
                    continue
                s = score(nx, ny)
                if s < best[0] or (s == best[0] and (dx, dy) < (best[1], best[2])):
                    best = (s, dx, dy)
        return [best[1], best[2]]
    else:
        # Evader: maximize distance to pursuer while trending to target corner; avoid obstacles.
        def score(nx, ny):
            d_opp = md(nx, ny, ox, oy)
            d_corner = md(nx, ny, target_corner[0], target_corner[1])
            obst = 1 if (nx, ny) in obstacles else 0
            return (-d_opp * 10 - d_corner) + obst * 1000
        best = (-10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if (nx, ny) in obstacles:
                    continue
                s = score(nx, ny)
                if s > best[0] or (s == best[0] and (dx, dy) < (best[1], best[2])):
                    best = (s, dx, dy)
        return [best[1], best[2]]