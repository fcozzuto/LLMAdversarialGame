def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def eval_pos(nx, ny):
        if not resources:
            tx, ty = (w - 1, h - 1) if (x + y) <= (ox + oy) else (0, 0)
            return cheb(nx, ny, ox, oy) * 1000 - (abs(tx - nx) + abs(ty - ny))
        best_take = -10**18
        best_deny = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            dp = cheb(ox, oy, rx, ry)
            if ds < dp:
                # take: win race, prefer nearer + bigger margin
                v = (dp - ds) * 120 - ds * 10
                if v > best_take: best_take = v
            elif dp < ds:
                # deny: make it harder for them (try to move toward closer-to-us while they're ahead)
                v = (ds - dp) * 80 - ds
                if v > best_deny: best_deny = v
            else:
                # tie-break: still try to be closer
                v = -ds
                if v > best_take: best_take = v
        # combine: ensure we still choose some move even if no take exists
        v = best_take if best_take > -10**17 else best_deny
        # additional shaping: avoid getting too close/locked around opponent (resource denier style)
        v += cheb(nx, ny, ox, oy) * 2
        # prefer moving into immediate resource if adjacent/equal distance
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) == 0:
                v += 300
                break
        return v

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        v = eval_pos(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]