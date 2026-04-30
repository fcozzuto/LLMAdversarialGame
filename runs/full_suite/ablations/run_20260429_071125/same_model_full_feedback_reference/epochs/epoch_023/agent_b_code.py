def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort(key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))  # deterministic

    best_dx, best_dy = 0, 0
    best_score = -10**18

    # Decide resources that maximize relative advantage; also counter opponent by focusing on their closest resources when behind.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base: how much sooner we can reach some resource than opponent can.
        best_adv = -10**18
        best_self_d = 10**9
        best_opp_d = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and (sd < best_self_d or (sd == best_self_d and od < best_opp_d))):
                best_adv, best_self_d, best_opp_d = adv, sd, od

        # If opponent is already much closer (best_adv < 0), bias toward reducing their lead by moving toward the opponent's closest resource(s).
        # If we're closer (best_adv >= 0), bias toward securing resources quickly.
        if best_adv >= 0:
            score = 1000 * best_adv - 3 * best_self_d
        else:
            score = 900 * best_adv + 2 * best_opp_d - 2 * best_self_d

        # Slight preference to move toward the "frontier" resource along our Chebyshev direction.
        # (Deterministic mild shaping)
        score += -0.1 * (abs(dx) + abs(dy))

        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]