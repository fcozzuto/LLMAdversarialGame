def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def edge_penalty(x, y):
        # small, deterministic preference to stay away from corners unless needed
        d = x + y
        d2 = (w - 1 - x) + (h - 1 - y)
        return d if d < d2 else d2

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = cheb(nx, ny, ox, oy)
        # Pursuer: minimize dist; Evader: maximize dist.
        # Tie-breakers: prefer not to edge-trap (evader) / prefer towards opponent (pursuer) via a small bias.
        if is_pursuer:
            val = dist * 1000 + (edge_penalty(nx, ny) * 0) + (-(nx - ox) * 0.001) + (-(ny - oy) * 0.001)
            better = best_val is None or val < best_val
        else:
            val = (-dist) * 1000 + (edge_penalty(nx, ny) * 1.0)  # bigger edge_penalty => better (farther from corners)
            better = best_val is None or val < best_val  # using negative dist, so smaller val means larger dist and larger edge_penalty
            # adjust: we encoded edge_penalty directly; smaller val prefers smaller edge_penalty, invert:
            # fix by flipping sign term:
            val = (-dist) * 1000 - (edge_penalty(nx, ny) * 1.0)
            better = best_val is None or val < best_val
        if better:
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]