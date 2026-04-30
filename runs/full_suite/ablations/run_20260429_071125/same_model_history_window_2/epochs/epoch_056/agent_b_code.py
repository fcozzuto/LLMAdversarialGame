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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources = sorted(resources)

    # Pick a small set of promising targets near us to keep it fast/deterministic
    near = []
    for tx, ty in resources:
        near.append((cheb(sx, sy, tx, ty), tx, ty))
    near.sort()
    targets = [(tx, ty) for _, tx, ty in near[:4]]

    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Advantage: how much closer we are than opponent to the best available target after our move
        # Also discourage stepping onto/adjacent to obstacles by harshly penalizing proximity.
        best_adv = -(10**18)
        for tx, ty in targets:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # If opponent is already closer or equal, prefer targets where we can overtake.
            adv = (d_opp - d_self) * 10
            # Slight preference for capturing sooner (lower self distance).
            adv += (6 - d_self)
            if d_self == 0:
                adv += 1000
            # If our move blocks the direct approach line to the nearest resource, boost.
            if (cheb(ox, oy, tx, ty) > 0) and (cheb(nx, ny, tx, ty) == cheb(sx, sy, tx, ty) - 1):
                adv += 2
            if adv > best_adv:
                best_adv = adv

        # Obstacle proximity penalty (avoid "pinning" against obstacles)
        prox = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if (ax, ay) in obstacles:
                    prox += 1
        val = best_adv - prox * 3

        if val > best[0]:
            best = (val, dx, dy)
        elif val == best[0]:
            # Deterministic tie-break: prefer staying slightly, then lexicographic by dx,dy
            if (dx, dy) < (best[1], best[2]):
                best = (val, dx, dy)

    return [int(best[1]), int(best[2])]