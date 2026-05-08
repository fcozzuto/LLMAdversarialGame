def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = set((int(p[0]), int(p[1])) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2)
    U = [(int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2]

    def is_opp_cell(x, y):
        return (x, y) in opp_set

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    # Heuristic:
    # 1) If we can capture opponent territory next step, do it (prefer closest).
    # 2) Otherwise, target unclaimed cells that are adjacent to opponent territory (frontier grab).
    # 3) Otherwise, expand toward center away from obstacles.
    center = (w // 2, h // 2)

    def frontier_score(x, y):
        # lower is better
        adj_opp = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_set:
                    adj_opp += 1
        # prefer nearer to us and not too close to obstacles
        min_obs = 10
        for (bx, by) in blocked:
            d = max(0, man(x, y, bx, by) - 1)
            if d < min_obs:
                min_obs = d
        return (0 if adj_opp > 0 else 1, man(sx, sy, x, y), -min_obs, abs(x - center[0]) + abs(y - center[1]), x, y)

    # Step evaluation
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue

        if is_opp_cell(nx, ny):
            key = (-1, man(nx, ny, ox, oy), nx, ny)  # immediate flip priority
        else:
            key = (0, 0, 0, 0)
            key = (1, frontier_score(nx, ny)[0], frontier_score(nx, ny)[1], frontier_score(nx, ny)[2], frontier_score(nx, ny)[3], nx, ny)

        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is not None:
        return best

    # Fallback (should be rare): move closer to center if possible
    cx, cy = center
    step_dx = 0 if sx == cx else (1 if cx > sx else -1)
    step_dy = 0 if sy == cy else (1 if cy > sy else -1)
    candidates = []
    for dx, dy in [(step_dx, 0), (0, step_dy), (step_dx, step_dy), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            candidates.append((man(nx, ny, cx, cy), dx, dy))
    candidates.sort()
    return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]