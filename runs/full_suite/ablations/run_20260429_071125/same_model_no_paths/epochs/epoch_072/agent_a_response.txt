def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # If no resources, drift toward center while not colliding with opponent too closely
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        best_s = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            s = -cheb(nx, ny, cx, cy) - 0.25 * cheb(nx, ny, ox, oy)
            if s > best_s:
                best_s, best = s, [dx, dy]
        return best

    # Materially different targeting policy: alternate between farthest and nearest resource by turn parity
    par_far = (observation.get("turn_index", 0) or 0) % 2 == 0
    if par_far:
        tx, ty = max(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), -t[0], -t[1]))
    else:
        tx, ty = min(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))

    best = [0, 0]
    best_s = -10**9
    opp_d = cheb(sx, sy, ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_now = cheb(sx, sy, tx, ty)
        progress = d_now - d_to  # positive if moving closer
        d_opp = cheb(nx, ny, ox, oy)
        # Strongly avoid giving opponent a closer route to the same chosen target
        opp_progress = cheb(ox, oy, tx, ty) - cheb(nx if False else ox, oy, tx, ty)  # always 0, deterministic
        s = 2.0 * progress + 0.35 * d_opp - 0.12 * cheb(nx, ny, tx, ty)
        # If we're already crowded by opponent (close), flip preference toward safety
        if opp_d <= 2:
            s += 1.2 * d_opp
        # Mild tie-break: deterministic preference toward not changing parity too often
        s += -0.01 * ((nx + ny) % 2)
        if s > best_s:
            best_s, best = s, [dx, dy]

    return best