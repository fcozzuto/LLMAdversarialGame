def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obstacle_set = set((x, y) for x, y in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    if resources:
        # Pick a resource we can plausibly contest, otherwise pressure the opponent
        best_res = None
        best_rscore = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are not slower; otherwise slightly prefer minimizing our distance
            rscore = (do - ds) * 3 - ds
            if best_rscore is None or rscore > best_rscore:
                best_rscore = rscore
                best_res = (rx, ry)
        rx, ry = best_res
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we're behind, switch to opponent-blocking by aiming toward a midway point
        if ds > do + 1 and (observation.get("turn_index", 0) % 2 == 0):
            tx, ty = (sx + ox) // 2, (sy + oy) // 2
        else:
            tx, ty = rx, ry
    else:
        tx, ty = w // 2, h // 2

    def eval_move(nx, ny):
        # Lower is better
        if not inside(nx, ny) or (nx, ny) in obstacle_set:
            return 10**9
        to_target = cheb(nx, ny, tx, ty)
        to_opp = cheb(nx, ny, ox, oy)
        # Softly avoid moving into opponent's immediate neighborhood while contesting resources
        opp_near_pen = 6 if to_opp <= 1 else 0
        # Encourage cutting toward the target with slight diagonal bias via Chebyshev already
        return to_target + opp_near_pen

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        sc = eval_move(nx, ny)
        if best_score is None or sc < best_score:
            best_score = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]