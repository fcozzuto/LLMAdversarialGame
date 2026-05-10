def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def step_risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and (nx, ny) in obstacles:
                    r += 1
        return r

    # Pick a resource where we are "ahead" (closer than opponent), with urgency.
    best_cell = None
    best_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Higher is better: prefer resources we can reach sooner; tie-break by self distance.
        # Add small urgency as turns run out.
        ahead = (od - sd)
        urgency = 1.0 / (1 + sd + (0 if turns_remaining is None else max(0, turns_remaining)) * 0.0)
        tie = -0.001 * sd
        val = 1000 * ahead + 10 * urgency + tie
        if val > best_val:
            best_val = val
            best_cell = (rx, ry)

    tx, ty = best_cell

    # One-step look: move to reduce distance to target while avoiding obstacles/near-obstacle dead-ends.
    cur_best = None
    cur_best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        # Also consider opponent pressure on target next turn.
        opp_nd = man(ox, oy, tx, ty) - 0  # unknown opponent move; use current distance as pressure proxy
        # Prefer reducing target distance; add small tie-break away from staying put if equal.
        v = -10 * nd + 0.5 * (od - opp_nd if False else 0)  # keep deterministic no-op
        v -= 2 * step_risk(nx, ny)
        v += -0.01 * (abs(nx - sx) + abs(ny - sy))
        # Encourage movement if it doesn't worsen distance.
        if nd == man(sx, sy, tx, ty):
            v += 0.02 * (dx != 0 or dy != 0)
        if v > cur_best_val:
            cur_best_val = v
            cur_best = (dx, dy)

    return [cur_best[0], cur_best[1]]