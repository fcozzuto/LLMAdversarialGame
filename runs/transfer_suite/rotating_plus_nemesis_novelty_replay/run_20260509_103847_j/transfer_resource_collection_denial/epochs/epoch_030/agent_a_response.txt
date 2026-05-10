def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose goal: prioritize resources where we are strictly closer; otherwise move to the opponent's nearest resource to deny.
    best_adv = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry); od = man(ox, oy, rx, ry)
        delta = sd - od
        if sd < od:
            key = (0, delta, sd, od, rx, ry)  # smallest (most negative delta), then shorter for us
            if best_adv is None or key < best_adv[0]:
                best_adv = (key, (rx, ry))

    if best_adv is not None:
        tx, ty = best_adv[1]
    else:
        # deny: opponent's nearest resource (tie by our distance smaller)
        best_den = None
        for rx, ry in resources:
            od = man(ox, oy, rx, ry); sd = man(sx, sy, rx, ry)
            key = (od, sd, rx, ry)
            if best_den is None or key < best_den[0]:
                best_den = (key, (rx, ry))
        tx, ty = best_den[1]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0); best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue
        ns = man(nx, ny, tx, ty)
        no = man(ox, oy, tx, ty)
        # drive to goal while trying to improve lead relative to opponent
        lead_after = ns - no  # smaller is better
        key = (lead_after, ns, abs(nx - tx) + abs(ny - ty), dx * dx + dy * dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]