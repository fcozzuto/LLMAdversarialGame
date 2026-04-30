def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = {(int(x), int(y)) for x, y in obstacles}
    res = [(int(x), int(y)) for x, y in resources]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs: c += 1
        return c

    cx, cy = w // 2, h // 2
    best_move = (0, 0); bestv = -10**18
    if res:
        # Prefer resources that you can reach much sooner than the opponent.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            e_obs = 2.0 * near_obs(nx, ny)
            # Evaluate best target for this hypothetical position.
            best_t = -10**18
            for rx, ry in res:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Margin: opponent arrival time advantage.
                t = (od - sd) - 0.35 * sd
                # Small bias toward nearer central lanes (more stable when tied).
                t -= 0.02 * (abs(rx - cx) + abs(ry - cy))
                if t > best_t: best_t = t
            # Encourage keeping separation while racing.
            sep = cheb(nx, ny, ox, oy)
            v = best_t + 0.25 * sep - e_obs
            if v > bestv:
                bestv = v; best_move = (dx, dy)
    else:
        # No resources: run to maximize distance from opponent while avoiding obstacles.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy) - 2.0 * near_obs(nx, ny) + 0.01 * (abs(nx - cx) + abs(ny - cy))
            if v > bestv:
                bestv = v; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]