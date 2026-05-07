def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # If opponent is very close to you, focus on immediate safe progress toward best still-uncontested resource.
    # Otherwise, prioritize the resource where you most beat the opponent's distance.
    best_targets = []
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd
        # Prefer resources we can reach sooner; margin tie-break by shorter self distance.
        best_targets.append((margin, -sd, rx, ry))

    best_targets.sort(reverse=True)
    # Try top few deterministically; choose one where we can improve our lead with one step.
    candidates = best_targets[:min(4, len(best_targets))]

    def pick_move_for_target(rx, ry):
        best = (-10**18, 10**18, None)  # (score, new_sd, move)
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not inside(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            new_sd = cheb(nx, ny, rx, ry)
            new_od = cheb(ox, oy, rx, ry)
            # Main: increase our lead. Secondary: reduce our distance. Tertiary: avoid stepping into "dead" cells (only by stability).
            score = (new_od - new_sd) * 100 - new_sd
            # Also slightly penalize moving away from the target when diagonals allowed.
            if new_sd > cheb(sx, sy, rx, ry):
                score -= 5
            if score > best[0] or (score == best[0] and new_sd < best[1]):
                best = (score, new_sd, (dxm, dym))
        return best[2]

    # Select target that maximizes eventual lead after one move; if tie, take closer to opponent-denial behavior:
    # prefer moves that reduce opponent's chance by pulling toward resources where opponent is relatively slower.
    close_threat = cheb(sx, sy, ox, oy) <= 2
    if close_threat:
        # Prefer immediate contested break: focus on resource where we are already closest.
        candidates = sorted(best_targets, key=lambda t: (-t[1], -t[0], t[2], t[3]))[:min(4, len(best_targets))]

    global_best = (-10**18, None)
    chosen = (0, 0)
    for margin, negsd, rx, ry in candidates:
        mv = pick_move_for_target(rx, ry)
        dxm, dym = mv
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        new_sd = cheb(nx, ny, rx, ry)
        new_od = cheb(ox, oy, rx, ry)
        lead = new_od - new_sd
        # Small deterministic bias: when equal lead, prefer moving in direction that gets x closer first (stable).
        bias = -abs((nx - rx)) + -abs((ny - ry))
        score = lead * 1000 - new_sd + bias
        if score > global_best[0]:
            global_best = (score, mv)
            chosen = mv

    return [int(chosen[0]), int(chosen[1])]