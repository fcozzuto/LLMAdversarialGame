def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles", []) or []
    obs = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role) or ("catcher" in role)

    t = int(observation.get("turn_index", 0) or 0)
    parity = t & 1

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    order_shift = parity  # deterministic small variation
    moves = moves[order_shift:] + moves[:order_shift]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def obstacle_proximity(x, y):
        # penalize moving adjacent to obstacles to reduce pathing collisions
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    prox += 1
        return prox

    # Evader wants far; Pursuer wants near. Both avoid obstacles.
    best = None
    best_score = -10**18 if pursuer else 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep in place on invalid move
        if (nx, ny) in obs:
            continue

        d = dist2(nx, ny)
        prox = obstacle_proximity(nx, ny)

        # One-step corner bias to help evade in open maps and help pursuit alignment.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        target = corners[(ox + oy + parity) & 3] if not pursuer else corners[(sx + sy + parity) & 3]
        corner_dist = (nx - target[0]) * (nx - target[0]) + (ny - target[1]) * (ny - target[1])

        if pursuer:
            # capture immediately if possible
            score = -(1000000 * (d == 0) + d) - 6 * prox + (-(corner_dist) // 20)
            # maximize
            if score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            score = 1000000 * (d == 0) - d - 6 * prox + (corner_dist // 20)
            # minimize (since score is inverted for distance; we set best for minimum via transform)
            if score < best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]