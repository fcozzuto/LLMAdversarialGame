def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role and "evad" in self_role) or ("pursuer" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def near_obs_pen(nx, ny):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (nx + dx, ny + dy) in obstacles:
                    pen += 1
        return pen

    if not self_is_pursuer:
        # Evader: maximize distance to pursuer and steer toward a far corner; avoid obstacles.
        tc = max(corners, key=lambda c: md(c[0], c[1], ox, oy))
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dist = md(nx, ny, ox, oy)
            steer = md(nx, ny, tc[0], tc[1])  # closer to target corner is good for survival plans
            val = dist * 10 - steer + near_obs_pen(nx, ny) * (-3)
            # If roles are uncertain, slightly prefer moving away from opponent diagonally/axis
            if ox == nx and oy == ny:
                val -= 50
            if best is None or val > bestv or (val == bestv and (dx, dy) < best):
                best, bestv = (dx, dy), val
        return list(best if best is not None else (0, 0))

    # Pursuer: greedy chase with obstacle-aware tie-break and corner-safety.
    tc = max(corners, key=lambda c: md(c[0], c[1], sx, sy))  # prefer not to get stuck away from space
    best = None
    bestv = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = md(nx, ny, ox, oy)
        corner_safety = -md(nx, ny, tc[0], tc[1])  # higher is better: closer to safer expansion corner
        val = dist * 10 - corner_safety + near_obs_pen(nx, ny) * 3
        # slight preference to reduce max coordinate movement when dist similar (stable deterministic)
        val += (abs(dx) + abs(dy)) * 0.1
        if best is None or val < bestv or (val == bestv and (dx, dy) < best):
            best, bestv = (dx, dy), val
    return list(best if best is not None else (0, 0))