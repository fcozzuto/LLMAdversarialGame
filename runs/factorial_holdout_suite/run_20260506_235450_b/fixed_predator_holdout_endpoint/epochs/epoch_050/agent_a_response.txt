def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9
    # Resource_denier tends to contest; so we pick resources where we create/maintain maximal distance advantage.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (dx != 0 or dy != 0) and not valid(nx, ny):
            continue

        my_opp_prox_pen = -cheb(nx, ny, ox, oy)  # discourage giving close contest proximity
        # Find best resource under our advantage model from this potential position.
        local_best = -10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d
            # Encourage immediate collection (my_d small) when advantage exists.
            val = adv * 10 - my_d
            # Slightly prefer resources that opponent is also not too close to (less denial pressure).
            val += -((opp_d + my_d) // 2) * 0.1
            if val > local_best:
                local_best = val

        score = local_best + my_opp_prox_pen
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]