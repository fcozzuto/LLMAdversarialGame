def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    if not resources:
        # Fall back: move toward opponent corner to contest center
        tx, ty = w-1-ox, h-1-oy
        best, bestv = [0, 0], -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx+dx, sy+dy
                if (dx != 0 or dy != 0) and inb(nx, ny) and (nx, ny) not in obstacles:
                    v = -dist((nx, ny), (tx, ty)) - 0.01*dist((nx, ny), (ox, oy))
                    if v > bestv: bestv, best = v, [dx, dy]
        return best if bestv > -10**8 else [0, 0]

    # Target selection: prefer resources we can reach no later than opponent; otherwise deny (opp far relatively)
    best_res = resources[0]
    best_lead = None
    closest_ds = None
    for r in resources:
        ds = dist((sx, sy), r)
        dop = dist((ox, oy), r)
        if ds <= dop:
            lead = 0
            if closest_ds is None or ds < closest_ds:
                closest_ds, best_res = ds, r
        else:
            lead = dop - ds
            if best_lead is None or lead > best_lead:
                best_lead, best_res = lead, r
    tx, ty = best_res

    # Move selection: step that reduces distance to target, avoids obstacles, lightly steers away from opponent
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx+dx, sy+dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]
    best = (0, 0)
    bestv = -10**18
    for dx, dy, nx, ny in moves:
        d_target = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        # Reward approaching target; penalize allowing opponent to get significantly closer
        opp_next = dist((ox, oy), (tx, ty)) - dist((nx, ny), (tx, ty))
        v = -d_target + 0.05*d_opp - 0.02*opp_next
        if dx == 0 and dy == 0:
            v -= 0.03
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return [int(best[0]), int(best[1])]