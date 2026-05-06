def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dsq(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx*dx + dy*dy

    if not resources:
        return [0, 0]

    # Strategy shift: target a resource where we have the biggest "distance advantage"
    # to avoid simply racing the nearest resource.
    best_r = resources[0]
    best_adv = -10**18
    for r in resources:
        rx, ry = r[0], r[1]
        sd = dsq(sx, sy, rx, ry)
        od = dsq(ox, oy, rx, ry)
        adv = od - sd
        # mild bias to closer targets among ties
        val = adv * 1.0 - 0.001 * sd
        if val > best_adv:
            best_adv = val
            best_r = (rx, ry)
    tx, ty = best_r

    # Choose next step that (1) reduces distance to chosen target,
    # (2) increases distance from opponent if we are at risk,
    # (3) respects obstacles.
    sd_now = dsq(sx, sy, tx, ty)
    od_to_target = dsq(ox, oy, tx, ty)
    risk = 1.0 if od_to_target < sd_now else 0.0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_t = dsq(nx, ny, tx, ty)
        d_o = dsq(nx, ny, ox, oy)
        # If opponent is nearer to target, we prioritize distancing while still moving towards it.
        score = (-d_t) + (risk * 0.02 * d_o) + (0.001 * d_o) - (0.0005 * d_t)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]