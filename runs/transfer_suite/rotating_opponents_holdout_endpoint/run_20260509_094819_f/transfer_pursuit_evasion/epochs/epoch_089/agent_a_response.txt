def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role", "pursuer")

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        dist = cheb(nx, ny, ox, oy)

        # pursuer wants smaller distance; evader wants larger distance
        if role == "evader":
            base = dist
            # bias toward keeping distance increasing on the dominant axis
            domx = abs(nx - ox)
            domy = abs(ny - oy)
            axis_bonus = 0.01 * (domx - domy)
            val = base + axis_bonus
        else:
            base = -dist
            # bias to reduce the dominant axis further (helps catch against corner evasion)
            domx0 = abs(sx - ox)
            domy0 = abs(sy - oy)
            dom_before = domx0 if domx0 > domy0 else domy0
            dom_after = abs(nx - ox) if abs(nx - ox) > abs(ny - oy) else abs(ny - oy)
            val = base + 0.05 * (dom_before - dom_after)

        # tie-break deterministically toward lower dx then lower dy for stability
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    if best is None:
        # fallback: allow staying put even if surrounded by obstacles
        return [0, 0]
    return [int(best[0]), int(best[1])]