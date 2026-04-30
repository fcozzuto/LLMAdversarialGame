def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    occ = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                occ.add((px, py))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in occ:
                resources.append((rx, ry))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a contest target: maximize (opp_dist - self_dist). Break ties by closer to center.
    if resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_t = None
        best_score = -10**18
        for tx, ty in resources:
            sd = dist(x, y, tx, ty)
            od = dist(ox, oy, tx, ty)
            center_bias = -0.01 * (abs(tx - cx) + abs(ty - cy))
            s = (od - sd) * 1000 + center_bias
            if s > best_score:
                best_score = s
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        # No visible resources: move toward opponent's side (opposite corner pressure)
        tx, ty = 0, 0

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        sd = dist(nx, ny, tx, ty)
        od = dist(ox, oy, tx, ty)

        # Main: decrease self distance while increasing opponent disadvantage.
        # Secondary: avoid moving onto squares that are closer to opponent than self (helps contention).
        self_to_opp = dist(nx, ny, ox, oy)
        cur_self_to_opp = dist(x, y, ox, oy)
        opp_disadv = (od - sd)

        # Small obstacle proximity penalty to avoid getting trapped.
        trap_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in occ:
                    trap_pen += 1

        val = opp_disadv * 2000 - sd * 3 - self_to_opp * 0.05 - trap_pen * 0.7 + (cur_self_to_opp - self_to_opp) * 0.2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]