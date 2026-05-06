def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(a, b): return 0 <= a < w and 0 <= b < h
    def blocked(a, b): return (a, b) in obstacles
    def man(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx + dy
    def sign(v): return 0 if v == 0 else (1 if v > 0 else -1)

    def eval_cell(nx, ny):
        # Prefer cells where we can reach some resource earlier than opponent by margin.
        best_margin = -10**9
        best_dist = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            margin = od - sd  # positive => we are closer
            if margin > best_margin or (margin == best_margin and sd < best_dist):
                best_margin = margin
                best_dist = sd
        # If we can't beat anyone, go for the contested resource that opponent is closest to,
        # but still slightly reduce distance to opponent.
        opp_d = man(nx, ny, ox, oy)
        if resources:
            od_min = min(man(ox, oy, rx, ry) for rx, ry in resources)
            return best_margin * 10 - best_dist + (od_min - opp_d) * 0.01
        return -man(nx, ny, ox, oy)

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best = (0, 0); best_val = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        v = eval_cell(nx, ny)
        if best_val is None or v > best_val or (v == best_val and (dx, dy) < best):
            best_val = v; best = (dx, dy)
    return [best[0], best[1]]