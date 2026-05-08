def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    self_role = (observation.get("self_role", "") or "").lower()
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def degree(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)
    best = None
    bestv = None

    # Deterministic tie-break: prefer moves with higher index in a fixed ordering from list.
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)
        deg = degree(nx, ny)
        # In a grid with obstacles, getting boxed in is costly; also steer toward/away from opponent.
        score = dist + (0.15 * deg if not is_evader else 0.25 * deg)
        # Add mild center pressure to reduce corner traps (evader) / help pursuer avoid stale cornering.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = d2(nx, ny, cx, cy)
        score += (-0.03 * center if is_evader else 0.01 * center)

        if best is None:
            best, bestv = (dx, dy), score
        else:
            better = score > bestv if is_evader else score < bestv
            if better or (score == bestv and i > moves.index(best)):  # deterministic fallback
                best, bestv = (dx, dy), score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]