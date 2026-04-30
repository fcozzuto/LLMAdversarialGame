def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Choose the most contested resource: maximize (opp_dist - self_dist)
    best_adv = None
    target = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd
        if best_adv is None or adv > best_adv or (adv == best_adv and sd < md(sx, sy, target[0], target[1])):
            best_adv = adv
            target = (rx, ry)

    if target is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    # Prefer moves that approach the target, avoid obstacles, and slightly steer away from opponent
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_t = md(nx, ny, tx, ty)
        d_opp = md(nx, ny, ox, oy)
        # If staying on top of opponent is possible, don't commit; keep a small separation.
        score = -d_to_t + 0.15 * d_opp
        # If target is current, stop moving to secure it.
        if (sx, sy) == (tx, ty):
            score += 0.5 if (dx, dy) == (0, 0) else -0.2
        # Tie-break deterministically: smaller dx then smaller dy
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]