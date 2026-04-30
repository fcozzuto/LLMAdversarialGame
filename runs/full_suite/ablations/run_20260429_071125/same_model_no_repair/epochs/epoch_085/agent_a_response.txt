def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def clamp01(n):
        return 1 if n > 0 else (-1 if n < 0 else 0)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Pick a primary target: where we can become relatively closer soon.
    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where opponent is farther (or we are much closer)
        key = (od - sd, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tr, ty = best_target

    # Second objective: deny opponent by moving toward the midpoint along the opponent->target line.
    midx = (ox + tr) // 2
    midy = (oy + ty) // 2

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Core: maximize relative gain over opponent on all resources (mostly the target)
        score = 0
        for i, (rx, ry) in enumerate(resources):
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            rel = od - sd  # higher is better for us
            # Bias strongly toward the chosen target; lightly toward others
            if (rx, ry) == (tr, ty):
                rel *= 3
                score += rel * 100
                # Also reward actually reaching quickly
                score += (6 - sd) * 8
            else:
                # small contribution from other resources to avoid dead-ends
                score += rel * 8
                score += clamp01(rel) * (2 if sd <= 2 else 0)

        # Deny objective: move to reduce opponent's ability to approach the target
        # Prefer positions closer to mid-point (but don't sacrifice too much target progress)
        mid_d = cheb(nx, ny, midx, midy)
        targ_d = cheb(nx, ny, tr, ty)
        score -= mid_d * 2
        score -= max(0, targ_d - cheb(sx, sy, tr, ty)) * 6

        # Tie-break: prefer fewer steps toward target, then toward denser resource proximity
        key = (score, -targ_d, -cheb(nx, ny, tr, ty), nx, ny)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]