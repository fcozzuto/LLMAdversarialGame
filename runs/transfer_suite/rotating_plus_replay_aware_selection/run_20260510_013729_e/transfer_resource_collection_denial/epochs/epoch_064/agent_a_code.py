def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick target with best "effective advantage": reward resources we're closer to, deny those they're closer to.
    best_target = None
    best_tval = -10**18
    for (rx, ry) in sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1])):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we can reach first, prioritize; if they can, prioritize denial (still move toward some contested resource).
        tval = 4.0 * (do - ds) - 0.20 * ds
        # If resource equals current cell (likely immediate capture), ensure it's top.
        if (sx, sy) == (rx, ry):
            tval += 10.0
        if tval > best_tval:
            best_tval = tval
            best_target = (rx, ry)

    tx, ty = best_target
    # Move choice: maximize immediate capture + reduce distance to chosen target, but also incorporate denial against opponent.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        cap = 2.5 if (nx, ny) == (tx, ty) else 0.0
        ns = cheb(nx, ny, tx, ty)
        nt = cheb(nx, ny, ox, oy)
        ds_before = cheb(sx, sy, tx, ty)
        # Encourage progress toward target; small tie-break to move generally toward opponent (denial) when contested.
        prog = 1.2 * (ds_before - ns)

        # Denial component: consider a few best contested resources deterministically.
        deny = 0.0
        for (rx, ry) in sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1]))[:6]:
            dsi = cheb(nx, ny, rx, ry)
            doi = cheb(ox, oy, rx, ry)
            lead = doi - dsi
            # Favor resources where we can beat them (positive lead), and mildly punish moving away from them.
            deny += 0.7 * lead / (1 + dsi)

        val = cap + prog - 0.10 * ns + 0.03 * nt + 0.9 * deny
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move