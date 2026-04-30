def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    best_targets = []
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we are closer to; slight bias to central/low coordinate for determinism.
        score = (do - ds) * 100000 - ds * 11 - (rx * 3 + ry)
        best_targets.append((score, rx, ry))
    best_targets.sort(reverse=True)
    _, tx, ty = best_targets[0]

    # If target cell is blocked, pick next best that isn't blocked.
    if (tx, ty) in obs and len(best_targets) > 1:
        for sc, rx, ry in best_targets[1:]:
            if (rx, ry) not in obs:
                tx, ty = rx, ry
                break

    # Estimate opponent "race" to the target by their next-step best reachable distance.
    def opp_min_dist_to_target():
        best = None
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                d = man(nx, ny, tx, ty)
                if best is None or d < best:
                    best = d
        if best is None:
            return man(ox, oy, tx, ty)
        return best

    opp_best_next = opp_min_dist_to_target()

    # Choose our move to minimize our distance to target and, secondarily, to prevent getting worse relative to opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_next = man(nx, ny, tx, ty)
        # Encourage immediate progress; strongly discourage letting opponent have a closer next reach.
        rel_after = opp_best_next - d_next
        # Minor tie-breaker to move deterministically toward larger x then y.
        tie = nx * 5 + ny
        val = rel_after * 10000 - d_next * 25 + tie * 0.001
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]