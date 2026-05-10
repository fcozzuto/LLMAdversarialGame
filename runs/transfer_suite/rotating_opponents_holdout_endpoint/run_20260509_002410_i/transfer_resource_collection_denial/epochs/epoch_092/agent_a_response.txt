def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # pick target: maximize advantage (opponent farther), else nearest resource
    best_t = None
    best_adv = -10**9
    best_near = 10**9
    for rx, ry in resources:
        d_me = md(sx, sy, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        adv = d_opp - d_me
        if adv > best_adv or (adv == best_adv and d_me < best_near):
            best_adv = adv
            best_near = d_me
            best_t = (rx, ry)

    # if no advantage, select nearest (deterministic already, but ensure)
    if best_adv <= 0:
        best_t = min(resources, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))

    tx, ty = best_t

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx if dx == 0 and dy == 0 else sx + dx
            ny = sy if dx == 0 and dy == 0 else sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))

    # choose move minimizing distance to target; tie-break by improving advantage after move
    chosen = None
    chosen_val = None
    for dx, dy, nx, ny in legal:
        d_me = md(nx, ny, tx, ty)
        d_opp = md(ox, oy, tx, ty)
        adv = d_opp - d_me
        val = (-adv, d_me, nx, ny, dx, dy)  # maximize adv, then minimize distance
        if chosen_val is None or val < chosen_val:
            chosen_val = val
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]