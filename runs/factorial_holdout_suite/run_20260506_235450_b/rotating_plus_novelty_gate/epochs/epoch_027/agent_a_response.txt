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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Target selection: prefer resources we can reach first; if none, pick one to contest.
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # positive means we're closer
        # Counter sweep behavior: bias toward rows away from opponent's current y
        row_bias = abs(ry - oy)
        # Slightly prefer parity shift to reduce same-row races
        parity_bias = -((ry - oy) & 1)
        key = (adv, -sd, row_bias, parity_bias)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Move selection: maximize progress to target while remaining safe; if tie, steer to make us closer than opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(nx, ny, ox, oy)
        # Higher is better: reduce our distance to target, and improve relative race vs opponent.
        # Also avoid moving onto squares that let opponent be much closer to the same target.
        cand_od_to_t = cheb(ox, oy, tx, ty)
        rel = cand_od_to_t - nsd
        val = (-nsd, rel, nod, -abs(ty - ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]