def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb_or_diagdist(ax, ay, bx, by):
        # Chebyshev distance matches diagonal-move grid
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_val = -10**18

    # Prefer actions that create a distance advantage over opponent for some resource
    # Also add small progress term toward opposite corner (1:1 with opposite starts).
    target_corner = (w - 1, h - 1) if (sx + sy) < (ox + oy) else (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # If opponent is closer to everything, minimize our worst-case lateness.
        worst_lateness = 10**18
        best_adv = -10**18

        for rx, ry in resources:
            ds = cheb_or_diagdist(nx, ny, rx, ry)
            do = cheb_or_diagdist(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            if ds == 0 and (nx, ny) == (rx, ry):
                adv = 10**6  # immediate pickup

            if adv < best_adv:
                pass
            if adv > best_adv:
                best_adv = adv

            lateness = ds - do  # negative is good (we're ahead)
            if lateness < worst_lateness:
                worst_lateness = lateness

        # Compose: primary maximize achievable advantage; secondary keep us advancing.
        prog = cheb_or_diagdist(nx, ny, target_corner[0], target_corner[1])
        # Lower prog is better; convert to negative.
        val = best_adv * 1000 + (-prog) * 3 + (-worst_lateness)

        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]