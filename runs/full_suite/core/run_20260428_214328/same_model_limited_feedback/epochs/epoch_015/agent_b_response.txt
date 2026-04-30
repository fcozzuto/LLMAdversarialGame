def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1,y1,x2,y2):
        dx = x1-x2
        if dx < 0: dx = -dx
        dy = y1-y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return (w//2, h//2)
        # Pick resource that we can reach sooner than opponent; also prefer farther-from-opponent for contest control.
        best = None
        bestv = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Primary: minimize (ds - do). Secondary: minimize ds. Tertiary: maximize (do - ds) again via value sign.
            v = (ds - do) * 1000 + ds
            if bestv is None or v < bestv:
                bestv = v
                best = (rx, ry)
        return best

    tx, ty = best_target()

    # If the chosen target is blocked off heavily, bias toward another that is safer next step.
    # (Lightweight: just allow step evaluation to handle obstacles.)
    def eval_pos(nx, ny):
        # Main: move closer to target.
        ds_next = cheb(nx, ny, tx, ty)
        ds_now = cheb(sx, sy, tx, ty)
        # Contest: also consider opponent reach to same target.
        do = cheb(ox, oy, tx, ty)
        # Slight preference for moves that don't give opponent advantage this turn.
        adv = ds_next - do
        # Small tie-break: prefer positions closer to any resource to prevent stalling.
        if resources:
            dmin = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
        else:
            dmin = 0
        # Prefer progress (reduce distance to target), avoid stagnation.
        return (adv * 1000 + ds_next) * 10 + (dmin if dmin is not None else 0) - (ds_now - ds_next)

    best_move = (0, 0)
    best_score = None
    # Deterministic move ordering for tie-break: aim roughly toward target, then stay.
    preferred = sorted(dirs, key=lambda d: (-(d[0]*(1 if tx>sx else -1 if tx<sx else 0)) - (d[1]*(1 if ty>sy else -1 if ty<sy else 0))))
    for dx, dy in preferred:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        score = eval_pos(nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # Fallback: if all moves blocked/out of bounds, stay.
    dx, dy = best_move
    return [int(dx), int(dy)]