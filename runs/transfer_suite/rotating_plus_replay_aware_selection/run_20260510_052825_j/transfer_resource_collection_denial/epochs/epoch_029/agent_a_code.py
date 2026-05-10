def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def man(ax, ay, bx, by):
        d1 = ax - bx
        d2 = ay - by
        if d1 < 0: d1 = -d1
        if d2 < 0: d2 = -d2
        return d1 + d2

    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    tr = observation.get("turns_remaining", 0)
    remcnt = observation.get("remaining_resource_count", len(valid))
    few = tr <= 5 or remcnt <= 3

    best = None
    best_val = None
    for rx, ry in valid:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        margin = od - sd
        value = margin * 2.0 - sd * 0.6
        if few:
            value += (-sd) * 0.15
        if sd <= 1:
            value += 2.5
        # deterministic tie-break toward center (2,2)-(5,5) region-ish
        cx, cy = 3.5, 3.5
        value += -0.01 * (abs(rx - cx) + abs(ry - cy))
        if best_val is None or value > best_val:
            best_val = value
            best = (rx, ry)

    tx, ty = best
    target = (tx, ty)

    def step_options():
        opts = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    opts.append((dx, dy))
        if not opts:
            return [(0, 0)]
        return opts

    def dist_after(dx, dy):
        return man(sx + dx, sy + dy, target[0], target[1])

    options = step_options()
    # Prefer moving closer; keep tie-break deterministic by fixed ordering.
    options.sort(key=lambda d: (dist_after(d[0], d[1]), d[1], d[0], 0 if (d[0], d[1]) == (0, 0) else 1))
    best_step = options[0]
    return [int(best_step[0]), int(best_step[1])]