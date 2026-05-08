def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def king_dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    scored = []

    # Opponent approximation: they move 1 king-step toward their nearest remaining resource.
    # We'll compute their "next distance" for each candidate resource.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_adv = -10**9
        # Choose the resource that gives us maximal advantage vs predicted opponent move.
        for rx, ry in resources:
            sd = king_dist(nx, ny, rx, ry)
            od = king_dist(ox, oy, rx, ry)
            od_next = od - 1 if od > 0 else 0  # predicted progress for opponent
            sd_next = sd - 1 if sd > 0 else 0  # our progress if we were one step closer
            adv = (od_next - sd_next)
            # Tie-break: prefer smaller our distance to that resource to secure pickup.
            if adv > best_adv:
                best_adv = adv
                best_sd = sd
            elif adv == best_adv:
                if sd < best_sd:
                    best_sd = sd

        scored.append((best_adv, best_sd, dx, dy))

    scored.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    return [scored[0][2], scored[0][3]]