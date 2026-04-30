def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Prefer advancing towards resources while discouraging obstacle-adjacent "wedges"
    best_move = [0, 0]
    best_score = None

    # Direction towards farthest resource corner bias (keeps motion meaningful)
    bias_dx = 1 if ox < sx else -1 if ox > sx else 0
    bias_dy = 1 if oy < sy else -1 if oy > sy else 0

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue

            # primary: closest resource distance after move
            dmin = 10**9
            tgt = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
                    tgt = (rx, ry)

            # if landing on a resource, strongly prefer
            hit_res = 1 if (nx, ny) in resources else 0

            # secondary: discourage moves that get too close to obstacles
            adj_ob = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax or ay:
                        if (nx + ax, ny + ay) in obstacles:
                            adj_ob += 1

            # mild: move generally away from opponent (agent_b tries to secure its own side)
            away_op = cheb(nx, ny, sx - bias_dx, sy - bias_dy)  # proxy: consistent directional pressure

            score = (-1000 * hit_res) + (-8 * dmin) + (-2 * adj_ob) + (1 * away_op)
            # tie-breaker: deterministic ordering already, but add tiny bias towards bias direction
            score += 0.1 * (dx * bias_dx + dy * bias_dy)

            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]