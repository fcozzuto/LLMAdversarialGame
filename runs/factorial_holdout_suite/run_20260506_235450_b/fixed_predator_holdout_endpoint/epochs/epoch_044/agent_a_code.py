def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    # Pick target by racing (favor resources we can reach strictly earlier).
    opp_dists = []
    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # key: prioritize "we arrive first", then maximize lead, then closer distance to us
        lead = od - sd
        arrives_first = 1 if sd < od else 0
        key = (arrives_first, lead, -sd, -(rx + 3 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose next step: move toward target, avoid obstacles; deterministically tie-break.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moves that reduce our chebyshev distance to target.
        d_to = cheb(nx, ny, tx, ty)
        # Secondary: keep away from opponent a bit if we're not winning the race.
        d_opp = cheb(nx, ny, ox, oy)
        d_self = cheb(nx, ny, tx, ty)
        # Determine urgency relative to best_key lead.
        # If we might be late (lead<=0), prioritize safer distance from opponent.
        late = 1 if best_key[1] <= 0 else 0
        val = (-(d_to), d_opp if late else 0, -abs(nx - tx) - abs(ny - ty), -(dx == 0 and dy == 0))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    # If all moves blocked (should be rare), stay.
    return [int(best_move[0]), int(best_move[1])]