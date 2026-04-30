def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if any(sx == rx and sy == ry for rx, ry in resources):
        return [0, 0]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # If no resources, run away from opponent while staying mobile.
    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            val = cheb(nx, ny, ox, oy)
            # small preference for not getting boxed in by obstacles
            free = sum(1 for ddx, ddy in deltas if valid(nx + ddx, ny + ddy))
            val = val * 10 + free
            if val > best[2]:
                best = (dx, dy, val)
        return [best[0], best[1]]

    # Choose a contested target: maximize how much closer we are than the opponent.
    best_res = None
    best_adv = -10**9
    best_selfd = 10**9
    for rx, ry in resources:
        selfd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        adv = oppd - selfd
        if adv > best_adv or (adv == best_adv and selfd < best_selfd):
            best_adv = adv
            best_selfd = selfd
            best_res = (rx, ry)

    tx, ty = best_res
    # If we're behind on all targets (adv <= 0), fall back to our closest resource.
    if best_adv <= 0:
        tx, ty = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))

    best_move = (0, 0, -10**9)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ourd = cheb(nx, ny, tx, ty)
        oppd_after = cheb(ox, oy, tx, ty)
        # Prefer reaching target sooner; also deny opponent by making our progress when we're not already behind.
        progress = (cheb(sx, sy, tx, ty) - ourd)
        val = progress * 100 - ourd
        if best_adv > 0:
            val += max(0, (oppd_after - ourd)) * 30
        # slight safety: move that increases distance from opponent (ties or when progress equal)
        val += cheb(nx, ny, ox, oy) * 0.5
        # obstacle awareness
        val += sum(1 for ddx, ddy in deltas if valid(nx + ddx, ny + ddy)) * 0.1
        if val > best_move[2]:
            best_move = (dx, dy, val)

    return [best_move[0], best_move[1]]