def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick best target by "reach before opponent": maximize (opp_dist - self_dist)
    best = None
    best_key = None
    opp_deltas = set()
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd  # higher means we can arrive earlier
        # Extra preference: nearer to our current line (good vs sweep-row behavior), still deterministic
        line_pref = -abs(ry - sy)
        key = (-(margin), -line_pref, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose among feasible deltas that improve our progress toward the target; avoid obstacles
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx
            ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                deltas.append((dx, dy))

    if not deltas:
        return [0, 0]

    cur_dist = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nd = cheb(nx, ny, tx, ty)
        # Primary: minimize resulting distance to target
        # Secondary: maximize our lead vs opponent on that same target
        sd_after = nd
        od_after = cheb(ox, oy, tx, ty)
        lead = od_after - sd_after
        # Tertiary: avoid drifting away in row (helps sweep-row matchups)
        val = (nd, -lead, abs(ny - sy), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move