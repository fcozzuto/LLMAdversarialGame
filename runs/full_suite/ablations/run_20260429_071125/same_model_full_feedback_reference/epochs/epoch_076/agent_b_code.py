def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: maximize advantage over opponent (who reaches first) with tie-breakers.
    best_t = None
    best_adv = None
    best_me = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        adv = d_opp - d_me  # higher => we are closer/equal sooner
        if best_t is None or adv > best_adv or (adv == best_adv and d_me < best_me):
            best_t = (rx, ry)
            best_adv = adv
            best_me = d_me

    # If no resources, drift toward opponent to contest center-ish (deterministic fallback).
    if best_t is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_t

    # Move choice: greedy step toward target, while not walking into obvious opponent approach.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)

        # Strongly prefer reaching the chosen target when adjacent.
        reach_bonus = -4 if (d_to_t == 0) else 0
        # Block preference: if we can't win quickly, increase our distance from opponent.
        block_term = 0.15 * d_to_o
        # If opponent is much closer to the target, also penalize moves that keep us equally close to them.
        d_opp_to_t = cheb(ox, oy, tx, ty)
        d_me_to_t = cheb(sx, sy, tx, ty)
        opp_closer = 1 if d_opp_to_t < d_me_to_t else 0
        opp_pen = (0.7 * opp_closer) * (cheb(nx, ny, tx, ty) - d_to_t)  # stays 0; keeps determinism if extended

        val = d_to_t + block_term + reach_bonus + opp_pen

        # Tie-break deterministically: prefer staying still only if it's not worse; then smallest dx,dy order.
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]