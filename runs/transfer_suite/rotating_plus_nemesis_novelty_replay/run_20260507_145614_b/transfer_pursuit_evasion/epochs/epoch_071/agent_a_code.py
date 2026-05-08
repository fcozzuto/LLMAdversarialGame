def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role", "pursuer")

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def min_obst_dist2(x, y):
        md = 10**9
        for (bx, by) in obst:
            d = dist2(x, y, bx, by)
            if d < md:
                md = d
                if md == 0:
                    return 0
        return md if md != 10**9 else 99**2

    candidates = []
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        man_opp = abs(nx - ox) + abs(ny - oy)
        align = 0
        if nx == ox or ny == oy:
            align = 1  # strong preference for alignment in pursuer role
        safety = min_obst_dist2(nx, ny)

        if role != "evader":
            # Pursuer: minimize distance, prefer alignment and avoiding obstacle proximity on ties
            key = (d_opp, man_opp, -align, -safety, dxm, dym)
            candidates.append((key, [dxm, dym]))
        else:
            # Evader: maximize distance; on ties, maximize safety and prefer moving away from opponent direction
            awayx = 1 if nx > ox else (-1 if nx < ox else 0)
            awayy = 1 if ny > oy else (-1 if ny < oy else 0)
            key = (-d_opp, -(abs(nx - ox) + abs(ny - oy)), -safety, -awayx, -awayy, dxm, dym)
            candidates.append((key, [dxm, dym]))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]