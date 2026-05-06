def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Bias toward resources while also keeping away from opponent (diagonal_probe pressure)
    if resources:
        cx = 0
        cy = 0
        for rx, ry in resources:
            cx += rx
            cy += ry
        cx = cx / float(len(resources))
        cy = cy / float(len(resources))
    else:
        cx, cy = (w - 1) * 1.0, (h - 1) * 1.0

    best = None
    best_tie = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            d_res = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < d_res:
                    d_res = d
        else:
            d_res = cheb(nx, ny, int(cx), int(cy))
        d_op = cheb(nx, ny, ox, oy)

        # If we're close enough to a resource, prioritize getting there quickly.
        res_term = -d_res
        opp_term = 0.06 * d_op

        # Encourage movement roughly toward resource centroid (deterministic).
        # (Use Chebyshev-like directional progress)
        dir_term = -0.02 * (cheb(nx, ny, int(cx), int(cy)) - cheb(sx, sy, int(cx), int(cy)))

        score = res_term + opp_term + dir_term

        # Deterministic tie-breaker: prefer diagonal when scores match, then smaller dx, then smaller dy.
        tie = (0 if dx != 0 and dy != 0 else 1, dx, dy)
        if best is None or score > best or (score == best and (best_tie is None or tie < best_tie)):
            best = score
            best_tie = tie

    if best is None:
        return [0, 0]
    return list(best_tie)[0:1] + [best_tie[2]] if best_tie[0] in (0, 1) else [0, 0]  # fallback safety