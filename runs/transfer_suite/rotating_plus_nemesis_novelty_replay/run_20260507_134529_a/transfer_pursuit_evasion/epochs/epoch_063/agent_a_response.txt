def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # deterministic tie-break: fixed order + numeric score
    def sign(a):
        return 1 if a > 0 else (-1 if a < 0 else 0)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        man = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        # obstacle clearance
        clearance = 0
        for ax, ay in obs:
            d = abs(nx - ax) + abs(ny - ay)
            if d == 0:
                clearance = -999
                break
            if d < 3:
                clearance -= (3 - d)
        # boundary pressure (keep away from edges slightly to reduce zigzag trapping)
        edge = 0
        if nx == 0 or nx == w - 1:
            edge -= 1
        if ny == 0 or ny == h - 1:
            edge -= 1

        if is_evader:
            # run from pursuer; prioritize increasing manhattan distance and escape to far corner
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_dist = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
            score = man * 2.0 + corner_dist * 0.05 + cheb * 0.2 + clearance * 0.2 + edge * 0.1
        else:
            # pursue; cut down distance, and prefer moves that reduce both manhattan and chebyshev
            tx = sign(ox - nx)
            ty = sign(oy - ny)
            alignment = 0
            if tx != 0 and ny == oy:
                alignment += 2
            if ty != 0 and nx == ox:
                alignment += 2
            score = -man * 2.2 - cheb * 0.6 + alignment * 0.2 + clearance * 0.1 + edge * 0.05

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]