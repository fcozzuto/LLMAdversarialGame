def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target scoring: prefer resources we reach earlier; break ties by favoring farther "pressure"
    # against resource_denier by not always taking the closest (helps avoid predictable grabs).
    best = None
    best_val = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer/slightly faster under chebyshev
        # discourage moving into our own "dead" edges late; encourage higher y then lower x deterministically
        edge_bias = (ry * 2 + (w - 1 - rx))
        val = (lead * 1000) + (edge_bias) - (sd * 3) + ((rx + ry) % 3)
        if best_val is None or val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_mval = None

    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # minimize distance to target; if equal, maximize "lead" improvement vs opponent deterministically
        dist = cheb(nx, ny, tx, ty)
        nd = cheb(ox, oy, tx, ty)
        lead_after = nd - dist
        # slight denier counter: prefer moves that also keep us away from opponent immediate collision zone
        block = cheb(nx, ny, ox, oy)
        mval = (-dist * 10) + (lead_after * 2) + (block * 0.01)
        # tie-break deterministic by preference order already stable; further tie by dx,dy
        if best_mval is None or mval > best_mval or (mval == best_mval and (dx, dy) < best_move):
            best_mval = mval
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]