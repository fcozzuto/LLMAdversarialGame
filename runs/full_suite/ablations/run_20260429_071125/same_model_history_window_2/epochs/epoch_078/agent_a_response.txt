def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_prox(x, y):
        if not obstacles:
            return 0
        best = 99
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick target by advantage over opponent, then bias toward higher obstacle-proximity-safety.
    best_t = None
    best_score = -10**9
    for tx, ty in resources:
        d_us = cheb(sx, sy, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        adv = d_op - d_us  # positive means we are closer/equal
        safety = obs_prox(tx, ty)  # prefer farther from obstacles
        score = 3 * adv + 0.15 * safety - 0.01 * (d_us + d_op)
        if score > best_score:
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t

    # Choose move maximizing improvement toward target while worsening opponent's approach.
    best_m = (0, 0)
    best_mscore = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_us_n = cheb(nx, ny, tx, ty)
            d_us_c = cheb(sx, sy, tx, ty)
            d_op_n = cheb(ox, oy, tx, ty)
            # If opponent were to move optimally next, approximate by our action affecting only their relative contest:
            # Use current opponent distance as baseline and penalize if we don't reduce ours.
            improve = d_us_c - d_us_n
            safety_here = obs_prox(nx, ny)
            # Strongly discourage moves that keep us from getting advantage.
            mscore = 5 * improve + 0.25 * safety_here - 0.02 * d_us_n - 0.01 * abs((d_op_n - d_us_n))
            if mscore > best_mscore:
                best_mscore = mscore
                best_m = (dx, dy)

    # If all moves were blocked (shouldn't happen), stay.
    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]