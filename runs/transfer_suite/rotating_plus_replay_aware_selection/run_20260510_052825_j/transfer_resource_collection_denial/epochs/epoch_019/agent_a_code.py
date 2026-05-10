def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    low_left = observation.get("remaining_resource_count", len(resources) if resources else 0)
    for r in resources:
        rx, ry = r[0], r[1]
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Opponent archetype: sweep_rows => penalize resources in/near opponent row.
        row_threat = abs(ry - oy)
        row_reward = row_threat if row_threat >= 2 else -2 * (2 - row_threat)
        # Encourage immediate claim when close; otherwise attack advantage window.
        immediate = 6 - sd
        # Prefer targets where we are faster, but strongly avoid where opponent is clearly faster.
        margin = od - sd
        if low_left <= 4:
            margin = margin * 1.2 + immediate * 0.6
        # If opponent is already close, bias to farther-row targets.
        if od <= 2:
            margin -= 1.5 * (2 - min(2, row_threat))
        cand = (margin + 0.35 * row_reward, -sd, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    rx, ry = best[2], best[3]
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # fallback: try axis-aligned move toward target that isn't blocked
        options = []
        if dx != 0 and (sx + dx, sy) not in obstacles:
            options.append([dx, 0])
        if dy != 0 and (sx, sy + dy) not in obstacles:
            options.append([0, dy])
        if dx != 0 and dy != 0 and (sx + dx, sy) not in obstacles:
            options.append([dx, 0])
        if dy != 0 and dx != 0 and (sx, sy + dy) not in obstacles:
            options.append([0, dy])
        return options[0] if options else [0, 0]

    return [dx, dy]