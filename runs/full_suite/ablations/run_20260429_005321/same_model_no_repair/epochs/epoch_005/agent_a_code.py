def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def on_resource(x, y):
        for rx, ry in resources:
            if rx == x and ry == y:
                return True
        return False

    # Pick best contested target (prefer ones we are not farther from than opponent)
    target = None
    best = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        key = (1 if sd <= od else 0, od - sd, -sd, -rx, -ry)
        # For sd<=od: prefer higher (od-sd), then closer; else prefer maximizing swing
        if best is None or key > best:
            best = key
            target = (rx, ry)

    if target is None:
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = target

    # Evaluate moves
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd = dist((nx, ny), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        swing_after = od - sd
        # Encourage immediate collection and contest advantage; penalize losing advantage
        score = 0
        if on_resource(nx, ny):
            score += 10000
        score += (1000 if sd <= od else 0)
        score += 20 * swing_after
        score += -3 * sd
        # Small bias toward reducing distance to opponent (to disrupt contests)
        score += -0.5 * dist((nx, ny), (ox, oy))
        # If we're behind on the target, penalize getting even more behind
        sd_now = dist((sx, sy), (tx, ty))
        if sd_now <= od:
            if sd > od:
                score -= 2000
        else:
            if sd > sd_now:
                score -= 50
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]