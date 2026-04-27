def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    # Target: prefer resource where we are not too behind; deterministic tie-break by distance sum
    target = None
    best_adv = -10**18
    for rx, ry in resources:
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = (do - dm)  # positive means we are closer
        # slight preference for nearer overall to keep it responsive
        score = adv * 1000 - (dm + do)
        if score > best_adv or (score == best_adv and (dm + do) < (cheb(sx, sy, target[0], target[1]) + cheb(ox, oy, target[0], target[1])) if target else False):
            best_adv = score
            target = (rx, ry)

    if target is None:
        target = (cx, cy)

    best_move = (0, 0)
    best_val = -10**18
    tx, ty = target

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        dmy = cheb(nx, ny, tx, ty)
        dmy0 = cheb(sx, sy, tx, ty)
        doy = cheb(ox, oy, tx, ty)

        # Our progress + deny opponent by preferring moves that reduce our distance more and (when close) cut off opponent
        progress = dmy0 - dmy
        our_dist_score = -dmy
        opp_dist_score = -doy
        # If we can move onto a resource immediately, prioritize strongly
        on_resource = 1 if (nx, ny) in resources else 0
        # Encourage moving toward center slightly to break standoffs
        center_bonus = -cheb(nx, ny, cx, cy) * 0.05

        val = progress * 200 + our_dist_score * 2 + opp_dist_score * 0.3 + center_bonus + on_resource * 1e6

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]