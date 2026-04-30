def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Deterministic ordering for tie-breaks
    resources.sort(key=lambda r: (r[0], r[1]))
    opp_corner_bias = 1 if (ox + oy) >= (w - 1 + h - 1 - (ox + oy)) else -1

    # Choose up to a few key targets/resources deterministically
    my_sorted = sorted(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    op_sorted = sorted(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))
    primary_targets = my_sorted[:3]
    opponent_threats = op_sorted[:3]

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Core: move toward our nearest likely reachable resources
        score = 0
        d0 = min(cheb(nx, ny, t[0], t[1]) for t in primary_targets)
        score += -3.0 * d0

        # Block: if we can reduce distance gap to a resource opponent is closest to, do it
        # (deterministic via same small opponent_threats set)
        gap_sum = 0.0
        for r in opponent_threats:
            d_op = cheb(ox, oy, r[0], r[1])
            d_me = cheb(nx, ny, r[0], r[1])
            if d_me <= d_op:
                gap_sum += (d_op - d_me)
        score += 1.2 * gap_sum

        # Safety/tempo: avoid moving too far from where we are currently progressing
        score += -0.2 * cheb(nx, ny, sx, sy)

        # Mild preference to drift away from opponent to avoid contested timing
        score += -0.08 * cheb(nx, ny, ox, oy) * opp_corner_bias * (-1)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]