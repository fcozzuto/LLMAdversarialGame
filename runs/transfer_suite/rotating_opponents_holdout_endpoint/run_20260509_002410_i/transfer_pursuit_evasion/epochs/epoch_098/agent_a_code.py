def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) or (role == "pursuer")

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # tie-break order: stable lexicographic on (score, dx, dy)
    best = None  # (score, dx, dy)

    cur_dist = cheb(sx, sy, ox, oy)
    # keep target: if evader, run to farthest corner; if pursuer, chase opponent directly
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if not pursuer:
        tx, ty = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), c[0] + c[1]))
    else:
        tx, ty = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        obs_pen = 0
        if (nx, ny) in obstacles:
            obs_pen = 1e6
        # also penalize adjacency to obstacles (helps vs wall-running trapping)
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj += 1

        # primary objective: distance to target (opponent or safe corner)
        d_to_target = cheb(nx, ny, tx, ty)
        if pursuer:
            # prioritize closing to opponent; slight preference for being closer than current
            d_change = cur_dist - cheb(nx, ny, ox, oy)
            score = (d_change * 100.0) + (10.0 / (1.0 + d_to_target)) - (5.0 * adj) - obs_pen
        else:
            # maximize distance from opponent; prefer increasing distance to opponent's position
            d_change = cheb(nx, ny, ox, oy) - cur_dist
            # also try to increase distance to chosen corner target (stays in escaping direction)
            score = (d_change * 100.0) + (5.0 / (1.0 + (cheb(nx, ny, tx, ty)))) - (3.0 * adj) - obs_pen

        if best is None or score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]