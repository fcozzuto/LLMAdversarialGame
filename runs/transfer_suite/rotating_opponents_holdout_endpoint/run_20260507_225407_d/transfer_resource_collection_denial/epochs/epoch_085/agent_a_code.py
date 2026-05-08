def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Different from pure racer: mix race-with-opponent-denial and "escape from tight obstacle influence"
    def risk(nx, ny):
        # penalize positions adjacent to obstacles (encourages path changes)
        r = 0
        for (ax, ay) in obstacles:
            if abs(nx - ax) <= 1 and abs(ny - ay) <= 1:
                r += 1
        return r

    # Choose target: maximize (opp - self) but also deny cells where opponent is ahead.
    best = None
    best_score = -10**9
    for rx, ry in resources:
        self_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        race = (opp_d - self_d)
        # deny boost if opponent closer; scale down if we're already close
        deny = (self_d - opp_d) if opp_d < self_d else 0
        # late-game: prioritize any reachable resource quickly
        urgency = -0.05 * self_d
        s = 2.0 * race + 1.5 * deny + urgency + 0.1 * (rem / (1 + len(resources)))
        if s > best_score:
            best_score = s
            best = (rx, ry)

    tx, ty = best
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_to_t = md(nx, ny, tx, ty)
            # also consider slightly increasing distance from opponent (denial by crowding)
            d_from_opp = md(nx, ny, ox, oy)
            candidates.append((d_to_t + 0.15 * (7 - d_from_opp), risk(nx, ny), dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda z: (z[0], z[1], z[2], z[3]))
    return [int(candidates[0][2]), int(candidates[0][3])]