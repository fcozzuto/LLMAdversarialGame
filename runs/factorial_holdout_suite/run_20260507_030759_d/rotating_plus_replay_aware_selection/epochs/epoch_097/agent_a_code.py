def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0:
        return [0, 0]

    # Choose a resource where we have a tempo advantage; otherwise choose a resource that is "least losing".
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        adv = d_opp - d_self  # positive means we are closer or equal (in Cheb metric)
        # Tie-break deterministically: higher adv, then smaller our distance, then lexicographic.
        key = (adv, -d_self, -(abs(rx - 3.5) + abs(ry - 3.5)), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Greedy step toward target with a preference to keep distance from opponent increasing.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self_next = cheb(nx, ny, tx, ty)
        d_opp_next = cheb(nx, ny, ox, oy)
        # Encourage reducing our distance to target; also discourage moving closer to opponent.
        # If we can reach the target this turn, prioritize it heavily.
        reach_bonus = 0
        if cheb(nx, ny, tx, ty) == 0:
            reach_bonus = 1000000
        val = (-d_self_next * 1000) + (d_opp_next * 3) + reach_bonus
        # Deterministic tie-break: smaller dx then dy then stay last.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]