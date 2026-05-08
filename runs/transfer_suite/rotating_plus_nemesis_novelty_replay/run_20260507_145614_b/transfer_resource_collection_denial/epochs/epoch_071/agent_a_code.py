def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def at_resource(x, y):
        for rx, ry in resources:
            if rx == x and ry == y:
                return True
        return False

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if at_resource(sx, sy):
        return [0, 0]

    # Choose target: either take the resource we're closest to, or if none, contest the one they are closest to.
    best_take = None
    best_contest = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if best_take is None or (od - sd, -sd, rx, ry) > (best_take[0], best_take[1], best_take[2], best_take[3]):
            best_take = (od - sd, -sd, rx, ry)
        if best_contest is None or (od - sd, sd, rx, ry) < (best_contest[0], best_contest[1], best_contest[2], best_contest[3]):
            best_contest = (od - sd, sd, rx, ry)

    # If we have any advantage (od - sd > 0), take the best advantaged; otherwise contest opponent's nearest.
    adv = best_take[0]
    if adv > 0:
        tx, ty = best_take[2], best_take[3]
    else:
        tx, ty = best_contest[2], best_contest[3]

    # Move selection: deterministic one-step toward target, but if multiple, prefer keeping distance from opponent.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        od_target = cheb(ox, oy, tx, ty)
        # Primary: minimize our distance to target after move (or preserve advantage).
        # Secondary: maximize distance from opponent to reduce their ability to contest next.
        score = (od_target - myd, -myd, cheb(nx, ny, ox, oy), -cheb(nx, ny, sx, sy), nx, ny)
        if best is None or score > best[0]:
            best = (score, dxi, dyi)

    if best is None:
        # fallback: stay if all moves blocked
        return [0, 0]
    return [best[1], best[2]]