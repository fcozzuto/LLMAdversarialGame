def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                rs.append((x, y))
    if not rs:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Pick move by maximizing "advantage" on the resource that we can reach best relative to opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_adv = -10**18
        best_self_d = 10**9

        for rx, ry in rs:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            # Favor resources where we are closer than opponent; small penalty for distance to reduce dithering.
            adv = (od - sd) * 1000 - sd
            if adv > best_adv or (adv == best_adv and sd < best_self_d):
                best_adv = adv
                best_self_d = sd

        # Secondary tie-break: also prefer actions that reduce our distance to the best_adv target (implicit in sd).
        score = best_adv
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]