def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obset.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obset

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    is_pursuer = "pursuer" in role or "pursue" in role or role == "pursuer"

    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # choose an evasive corner deterministically for tie-breaking
    far_corner = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), -c[0], -c[1]))

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)

        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obset:
                    adj_obs += 1

        # small penalty for stepping "towards" opponent when evading; small bonus when pursuing
        approach = cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)

        # barrier proxy: discourage being adjacent to obstacles (often gets trapped by zigzags)
        wall_pen = adj_obs * 0.8

        # corner shaping
        corner_dist = cheb(nx, ny, far_corner[0], far_corner[1])
        opp_corner_dist = cheb(sx, sy, far_corner[0], far_corner[1])
        corner_change = corner_dist - opp_corner_dist

        if is_pursuer:
            # minimize distance; also prefer moves that reduce corner distance away from evader-corner only slightly
            s = (-d) * 100.0 + (5 - adj_obs) * 2.0 + (-approach) * 0.5 + (-corner_change) * 0.05
        else:
            # maximize distance; prefer moving toward far_corner in chebyshev sense
            s = (d) * 100.0 - wall_pen + (corner_change * -1.0) * 0.2 + (-approach) * 0.05

        # deterministic tie-break
        s += -(nx * 17 + ny * 31)

        if best_score is None or s > best_score:
            best_score = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]