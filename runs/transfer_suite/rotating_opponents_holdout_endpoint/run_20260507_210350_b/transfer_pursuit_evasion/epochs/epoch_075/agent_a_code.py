def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    role_opp = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = any(k in role_self for k in ("pursuer", "chaser", "hunter"))
    opp_is_pursuer = any(k in role_opp for k in ("pursuer", "chaser", "hunter"))
    i_am_pursuer = self_is_pursuer if (self_is_pursuer or opp_is_pursuer) else True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # 0th-order "pathing": choose move that improves/maintains direction while avoiding blocks and "wall hugging".
    best_score = None
    best_move = (0, 0)
    far_corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        # primary objective: capture pressure / evasion distance
        dist_now = cheb(nx, ny, ox, oy)

        # secondary: avoid dead-ends near obstacles
        neigh_blocks = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx, ty = nx + adx, ny + ady
                if inb(tx, ty) and blocked(tx, ty):
                    neigh_blocks += 1

        # tertiary: corner bias (only for evader to exploit 8-neighbor capture dynamics)
        corner_target_score = 0
        if not i_am_pursuer:
            corner_target_score = max(cheb(nx, ny, cx, cy) for cx, cy in far_corners)

        # deterministic tie-break: prefer lexicographically smaller move deltas when scores equal
        if i_am_pursuer:
            score = -dist_now - 0.08 * neigh_blocks + 0.001 * (dx + 2 * dy)
        else:
            score = dist_now + 0.10 * corner_target_score - 0.08 * neigh_blocks + 0.001 * (dx + 2 * dy)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If all candidate moves invalid, stay still.
    return [int(best_move[0]), int(best_move[1])]