def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy  # Manhattan for determinism

    # Pick a target resource that we can beat the opponent to (maximize opp_dist - self_dist).
    best_t = None
    best_adv = -10**9
    for r in resources:
        if r in obstacles:
            continue
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        adv = od - sd
        # Small preference to nearer resources when tied.
        if adv > best_adv or (adv == best_adv and sd < dist((sx, sy), best_t) if best_t else True):
            best_adv = adv
            best_t = r

    # If no resources, drift toward center to deny space.
    if best_t is None:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        # Choose the move minimizing distance to center (Chebyshev-like via manhattan).
        target = (tx, ty)
        dxs = [1, 0, -1]
        dys = [1, 0, -1]
    else:
        target = best_t
        dxs = [1, 0, -1]
        dys = [1, 0, -1]

    cand = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            if target == best_t:
                nd = dist((nx, ny), best_t)
                # Also consider whether moving keeps the opponent away from our target.
                nod = dist((ox, oy), best_t)
                # Score our resulting advantage.
                adv2 = nod - nd
                cand.append((nd, -adv2, dx, dy))
            else:
                # center as float; use manhattan approx with rounding.
                cx, cy = int(target[0] + 0.5), int(target[1] + 0.5)
                nd = dist((nx, ny), (cx, cy))
                cand.append((nd, 0, dx, dy))

    if not cand:
        return [0, 0]

    cand.sort()
    _, _, dx, dy = cand[0]
    return [dx, dy]