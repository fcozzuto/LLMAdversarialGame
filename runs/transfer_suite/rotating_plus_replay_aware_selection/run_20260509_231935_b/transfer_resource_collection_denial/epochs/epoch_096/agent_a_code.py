def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res_raw = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs_raw if p and len(p) >= 2}
    resources = [(p[0], p[1]) for p in res_raw if p and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        best = (1e18, 1e18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            risk = 0
            for kx in (-1, 0, 1):
                for ky in (-1, 0, 1):
                    if kx == 0 and ky == 0:
                        continue
                    if (nx + kx, ny + ky) in obstacles:
                        risk += 1
            v = (man(nx, ny, ox, oy), risk, 0, dx)
            if v < best:
                best = v
        return [best[2], best[3]]

    # Choose the resource that maximizes our advantage (lower "we-lead value"),
    # then move one step toward it.
    best_r = None
    best_key = (1e18, 1e18)
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; penalize those opponent is closer to.
        lead = ds - 0.85 * do
        key = (lead, ds)
        if key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # If we can take the resource immediately, do so.
    if man(sx, sy, rx, ry) == 0:
        return [0, 0]

    # Evaluate next moves toward chosen target with obstacle/risk penalty.
    best = (1e18, 1e18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_next = man(nx, ny, rx, ry)
        opp_next = man(nx, ny, ox, oy)
        # Risk: avoid being adjacent to obstacles.
        risk = 0
        for kx in (-1, 0, 1):
            for ky in (-1, 0, 1):
                if kx == 0 and ky == 0:
                    continue
                if (nx + kx, ny + ky) in obstacles:
                    risk += 1
        # Small tie-break to not drift toward opponent unnecessarily.
        v = (ds_next - 0.08 * opp_next + 0.6 * risk, risk, ds_next, dx * 2 + dy)
        if v < best:
            best = v
            best_dx, best_dy = dx, dy
    return [best_dx, best_dy]