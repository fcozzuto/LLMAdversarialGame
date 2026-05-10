def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    rolestr = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in rolestr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def clamp01(v):
        return 0 if v < 0 else 1 if v > 1 else v

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Choose a deterministic target corner for evasion / pursuit bias
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    if is_evader:
        # target farthest corner from opponent
        cx, cy = max(corners, key=lambda t: dist2(t[0], t[1], ox, oy))
    else:
        # target nearest corner to opponent (reduces opponent safe hopping)
        cx, cy = min(corners, key=lambda t: dist2(t[0], t[1], ox, oy))

    def obstacle_density(nx, ny):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in obs:
                    cnt += 1
        return cnt

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, cx, cy)
        d_corner_opp = dist2(ox, oy, cx, cy)

        # Greedy move with corner bias and obstacle aversion; deterministic tie-break via move sorting
        # Evader: maximize distance to opponent and try to move toward the chosen corner.
        # Pursuer: minimize distance to opponent and try to stay between opponent and the chosen corner.
        dens = obstacle_density(nx, ny)

        if is_evader:
            score = d_opp * 10 - d_corner * 0.35 + (d_corner_opp - d_corner) * 1.2 - dens * 0.8
        else:
            # If opponent is moving away toward corners, bias toward intercept-like behavior by reducing
            # opponent's "corner potential" relative to our corner target.
            score = (-d_opp) * 10 - d_corner * 0.15 + (d_corner_opp - d_corner) * 0.8 - dens * 0.5

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]