def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    allowed = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # fallback: move away from opponent slightly to avoid collision blocking
        best = (10**9, 0, 0)
        for dx, dy in allowed:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            # prefer increasing distance; tie-breaker toward center
            score = (-d, abs(nx - w // 2) + abs(ny - h // 2))
            if score < best[:2]:
                best = (score[0], dx, dy)
        return [best[1] if best[1] or best[1] == 0 else 0, best[2] if best[1] or best[2] == 0 else 0]

    best_res = None
    best_val = None
    parity = observation.get("turn_index", 0) % 2
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Even turns: prioritize resources opponent is far from (defensive/safer).
        # Odd turns: prioritize resources opponent is close to, to contest (offensive adjustment).
        base = (do - ds)
        if parity == 0:
            val = (-ds) + 0.5 * base
        else:
            val = (0.7 * base) - 0.1 * ds
        # Tie-break: closer to self (deterministic)
        key = (-(val), ds, rx, ry)  # min
        if best_val is None or key < best_val:
            best_val = key
            best_res = (rx, ry)

    tx, ty = best_res
    best_move = (10**9, 0, 0, 0)  # (dist_to_target, manh_to_target, -dist_to_opp, dx, dy)
    for dx, dy in allowed:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dt = cheb(nx, ny, tx, ty)
        # small tie-breakers
        md = abs(nx - tx) + abs(ny - ty)
        da = cheb(nx, ny, ox, oy)
        cand = (dt, md, -da, dx, dy)
        if cand < best_move:
            best_move = cand

    # If blocked (shouldn't), stay.
    if best_move[3] == 0 and best_move[4] == 0 and ((sx, sy) in obstacles):
        return [0, 0]
    return [int(best_move[3]), int(best_move[4])]