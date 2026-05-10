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

    def adj_any_set(x, y, s):
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in s:
                return True
        return False

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in self_ter:
            base = 0.0
        else:
            base = 0.0
        if (x, y) in opp_ter:
            base += 2.5
        if (x, y) in unclaimed:
            base += 1.25
        if (x, y) not in self_ter and not (x, y) in opp_ter:
            base += 0.1  # steer toward expansion when possible

        # Prefer expanding from our territory (frontier) and reducing distance to opponent
        if self_ter and adj_any_set(x, y, self_ter):
            base += 0.9
        if opp_ter and adj_any_set(x, y, opp_ter):
            base += 0.7

        d_self = abs(x - sx) + abs(y - sy)
        d_op = abs(x - ox) + abs(y - oy)
        # Mild preference toward moving away from our own to new territory and toward opponent contact
        base += 0.15 * (5 - d_self)
        base += 0.35 * (8 - d_op)  # larger when closer to opponent

        # Avoid committing if it requires stepping into a cell far from both frontiers
        if not self_ter and not opp_ter:
            base += 0.0
        elif (x, y) not in self_ter and not adj_any_set(x, y, self_ter) and not adj_any_set(x, y, opp_ter):
            base -= 0.6
        return base

    best = None
    best_move = [0, 0]
    # Deterministic tie-break: smallest (dx, dy) lex among dirs after max score
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        key = (sc, -abs(nx - ox) - abs(ny - oy), -abs(nx - sx) - abs(ny - sy))
        if best is None or key > best or (key == best and (dx, dy) < tuple(best_move)):
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]