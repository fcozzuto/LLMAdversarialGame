def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def sqd(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx*dx + dy*dy
    def pick_target(x, y):
        best = None; best_k = None
        for rx, ry in resources:
            if (rx, ry) in obstacles: 
                continue
            sd = sqd(x, y, rx, ry)
            # prefer closer, and if tie, prefer "more central" resources to reduce detours vs row sweeps
            cx = abs(rx - (w-1)/2); cy = abs(ry - (h-1)/2)
            k = (sd, cx+cy, rx, ry)
            if best_k is None or k < best_k:
                best_k = k; best = (rx, ry)
        return best

    def eval_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return (10**18, 10**18)
        # Assume opponent pursues its own nearest target (deterministic) to contest the same resources.
        ot = pick_target(ox, oy)
        # If opponent already has no valid target, prioritize our nearest resource.
        best_adv = -10**18
        best_ours = 10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our = sqd(nx, ny, rx, ry)
            opp = sqd(ox, oy, rx, ry)
            # advantage: opponent farther is better. Small bias favors picking a resource that is also near our next step.
            adv = opp - our
            if ot == (rx, ry):
                adv += 0.6  # increase pressure on opponent's current target
            if adv > best_adv or (adv == best_adv and our < best_ours):
                best_adv = adv; best_ours = our
        # Primary: maximize advantage; Secondary: minimize our distance to the chosen best resource; Tertiary: minimize displacement.
        disp = abs(dx) + abs(dy)
        return (-best_adv, best_ours, disp)

    best = None; best_k = None
    for dx, dy in deltas:
        k = eval_move(dx, dy)
        if best_k is None or k < best_k:
            best_k = k; best = (dx, dy)
    return [int(best[0]), int(best[1])]