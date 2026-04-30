def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    if resources:
        # Choose a target deterministically: best "reach advantage" vs opponent.
        tx, ty = resources[0]
        best_t = -10**18
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            t = (do - ds) * 4 - ds
            if rx > tx or (rx == tx and ry > ty):
                pass
            if t > best_t:
                best_t = t
                tx, ty = rx, ry

        # One-step evaluation: move toward target while also moving away from opponent's ability.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            ds1 = man(nx, ny, tx, ty)
            ds0 = man(sx, sy, tx, ty)
            opp0 = man(ox, oy, tx, ty)
            opp1 = man(ox, oy, tx, ty)  # unchanged this turn; keep term stable
            # Include opponent distance to our target-area (using a proxy: how close opponent is to the target after we approach).
            opp_to = man(ox, oy, nx, ny)
            # Prefer reducing our distance to target, penalize moving closer to opponent (to avoid contention), tie-break by lexicographic delta.
            val = (ds0 - ds1) * 20 + (opp0 - opp1) * 2 + (-opp_to) * 0.1 + (-(abs(nx - tx) + abs(ny - ty))) * 0.01
            if val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]