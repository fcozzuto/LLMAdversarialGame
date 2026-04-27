def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): return abs(a - c) + abs(b - d)
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    if not resources:
        # No resources: move to maximize distance from opponent while avoiding obstacles
        best, bestsc = [0, 0], -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            sc = md(nx, ny, ox, oy)
            if sc > bestsc: bestsc, best = sc, [dx, dy]
        return best
    # Pick our best resource by minimizing (our_dist - opp_dist)
    def score_res(px, py, rx, ry):
        d1, d2 = md(px, py, rx, ry), md(ox, oy, rx, ry)
        return (d1 - d2, d1)
    t1 = min(resources, key=lambda r: score_res(sx, sy, r[0], r[1]))
    # Pick opponent's best resource similarly, then intercept from our side
    t_op = min(resources, key=lambda r: score_res(ox, oy, r[0], r[1]))
    tx, ty = t_op
    # Intercept: one step from opponent toward their target, otherwise the target if already close
    stepx = 0 if ox == tx else (1 if tx > ox else -1)
    stepy = 0 if oy == ty else (1 if ty > oy else -1)
    ix, iy = ox + stepx, oy + stepy
    if not valid(ix, iy):
        ix, iy = tx, ty
    if not valid(ix, iy):
        ix, iy = ox, oy
    best, bestsc = [0, 0], -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        # Move toward our resource, but also toward intercept to deny opponent progress
        d1 = md(nx, ny, t1[0], t1[1])
        d2 = md(nx, ny, ix, iy)
        # Prefer not to give opponent a closer path: slight penalty if we move closer to them
        dO = md(nx, ny, ox, oy)
        sc = (-2.0 * d1) + (-1.2 * d2) + (0.15 * dO)
        if sc > bestsc: bestsc, best = sc, [dx, dy]
    return best