def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh: 
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate best "race" target after this move
        v = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            if nx == rx and ny == ry:
                sc = 10**9 + (cheb(ox, oy, rx, ry) - 0)
            else:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer targets where we can arrive earlier; if none, reduce damage by targeting where we are closest.
                win = (ds <= do)
                sc = (do - ds) * (4000 if win else -1200) - ds * 5 - (0 if win else do * 2)
                if ds == 0: sc += 5000
            if sc > v:
                v = sc

        # Secondary tie-break: prefer moves that reduce our distance to the nearest resource
        if v == best_val:
            cur_near = min(cheb(sx, sy, r[0], r[1]) for r in resources if (r[0], r[1]) not in obstacles)
            new_near = min(cheb(nx, ny, r[0], r[1]) for r in resources if (r[0], r[1]) not in obstacles)
            if new_near < cur_near:
                best_move = [dx, dy]
                continue
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move