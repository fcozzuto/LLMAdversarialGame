def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    my_par = (sx + sy) & 1
    best_move = [0, 0]
    best_score = -10**9

    for dxm in (-1, 0, 1):
        for dym in (-1, 0, 1):
            nx, ny = sx + dxm, sy + dym
            if not is_free(nx, ny):
                continue

            # Evaluate by the best resource we can secure soonest after moving.
            best_for_move = None
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)

                # Encourage grabbing resources that we are closer to than opponent,
                # but avoid moves that only match by parity/oscillation.
                adv = od - sd
                parity_bonus = 1 if (((rx + ry) & 1) == my_par) else 0
                # If opponent is very close to a resource, deprioritize it.
                opp_pressure = 6 - od if od <= 6 else 0
                key = 5 * adv - sd + 0.75 * parity_bonus - 0.6 * opp_pressure
                if best_for_move is None or key > best_for_move:
                    best_for_move = key

            if best_for_move is None:
                best_for_move = 0
            if best_for_move > best_score:
                best_score = best_for_move
                best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]