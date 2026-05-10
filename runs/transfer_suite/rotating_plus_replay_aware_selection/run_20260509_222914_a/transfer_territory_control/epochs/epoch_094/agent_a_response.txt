def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_to_self(x, y):
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            if (x + dx, y + dy) in self_ter:
                return True
        return False

    def adj_to_opp(x, y):
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            if (x + dx, y + dy) in opp_ter:
                return True
        return False

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        if cell in self_ter:
            base = 1.0
        elif cell in opp_ter:
            base = 12.0
        elif cell in unclaimed:
            base = 6.0
        else:
            base = 0.5

        frontier = 0.0
        if (nx, ny) in unclaimed and adj_to_self(nx, ny):
            frontier += 20.0
        if (nx, ny) in unclaimed and adj_to_opp(nx, ny):
            frontier += 5.0

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)

        score = base + frontier + (2.0 / (1.0 + dist_to_opp)) - 0.15 * dist_center
        if best is None or score > best + 1e-9:
            best = score
            best_move = [dx, dy]
        elif best is not None and abs(score - best) <= 1e-9:
            # deterministic tie-break: prefer closer to opponent, then smaller dx, then smaller dy, then stay
            tb = (abs(nx - ox) + abs(ny - oy), abs(dx), abs(dy), 0 if dx == 0 and dy == 0 else 1)
            ob = (abs((sx + best_move[0]) - ox) + abs((sy + best_move[1]) - oy), abs(best_move[0]), abs(best_move[1]), 0 if best_move[0] == 0 and best_move[1] == 0 else 1)
            if tb < ob:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]