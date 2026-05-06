def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if legal(x, y):
                    rpos.append((x, y))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if legal(x, y):
                rpos.append((x, y))

    if not legal(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if legal(sx + dx, sy + dy):
                    return [dx, dy]
        return [0, 0]
    if not rpos:
        return [0, 0]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)] + [(0, 0)]
    candidates = []
    for (rx, ry) in rpos:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; break ties by larger current advantage potential
        priority = (0 if ds <= do else 1, ds - do, rx + ry)
        candidates.append((priority, rx, ry))
    candidates.sort(key=lambda t: t[0])
    targets = [(t[1], t[2]) for t in candidates[:6]]

    def best_step_for_target(rx, ry):
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            new_ds = md(nx, ny, rx, ry)
            new_do = md(ox, oy, rx, ry)
            # Move closer while discouraging giving opponent a strictly better approach
            score = -new_ds + 0.35 * (new_do - new_ds) + 0.08 * md(nx, ny, ox, oy)
            # Small deterministic bias to avoid oscillations: favor dx,dy towards target
            score += 1e-6 * (dx * (1 if rx > nx else (-1 if rx < nx else 0)) + dy * (1 if ry > ny else (-1 if ry < ny else 0)))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return best[1:] if best else (0, 0)

    # If very close to a resource, lock onto it; else choose best among prioritized targets
    near = min(rpos, key=lambda p: md(sx, sy, p[0], p[1]))
    if md(sx, sy, near[0], near[1]) <= 1:
        return list(best_step_for_target(near[0], near[1]))

    best_overall = None
    for (rx, ry) in targets:
        dx, dy = best_step_for_target(rx, ry)
        nx, ny = sx + dx, sy + dy
        ds = md(nx, ny, rx, ry)
        do = md(ox, oy, rx, ry)
        overall = -ds + 0.55 * (do - ds) + 0.1 * md(nx, ny, ox, oy)
        if best_overall is None or overall > best_overall[0]:
            best_overall = (overall, dx, dy)

    if best_overall:
        return [best_overall[1], best_overall[2]]

    return [0, 0]