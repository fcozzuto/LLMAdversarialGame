def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Race heuristic: prefer resources we can reach sooner than opponent; otherwise head toward best still-possible.
    best = None
    best_val = None
    for dx, dy, nx, ny in legal:
        self_better = 10**9
        val_here = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # If we can arrive earlier, strong reward; if not, penalize heavily by how much later.
            arrival_diff = od - sd  # positive means we're earlier
            score = 0
            if arrival_diff > 0:
                score = -sd - 3 * arrival_diff
            elif arrival_diff == 0:
                score = -sd - 2
            else:
                score = 50 + (sd - od) * 5
            # Small tie-break toward closer resources.
            score += sd * 0.05
            if val_here is None or score < val_here:
                val_here = score
        if val_here is None:
            continue
        # Prefer smaller val_here; deterministic tie-break by move order.
        if best_val is None or val_here < best_val:
            best_val = val_here
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]