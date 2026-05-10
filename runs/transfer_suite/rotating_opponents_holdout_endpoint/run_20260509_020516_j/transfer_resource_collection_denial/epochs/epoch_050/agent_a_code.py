def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonals allowed)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        self_pos = (nx, ny)
        s = -10**18
        for rx, ry in resources:
            rpos = (rx, ry)
            ds = dist(self_pos, rpos)
            do = dist((ox, oy), rpos)
            # Prefer resources where we arrive sooner; slight preference for being closer overall
            val = (do - ds) * 10 - ds
            if val > s:
                s = val

        # Tie-break: prefer moves that reduce distance to the currently best resource (deterministic)
        if s > best_score:
            best_score = s
            best_move = (dx, dy)
        elif s == best_score:
            # deterministic tie: smaller dist to closest resource
            cur_best_ds = min(dist((sx + best_move[0], sy + best_move[1]), r) for r in resources)
            cand_best_ds = min(dist((nx, ny), r) for r in resources)
            if cand_best_ds < cur_best_ds:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]