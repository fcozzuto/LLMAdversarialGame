def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]
    if w <= 0 or h <= 0:
        return [0, 0]

    # If no resources, move to maximize distance from opponent deterministically.
    if not resources:
        best = (0, 0)
        bestd = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d > bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18

    # Evaluate each move by the immediate "win margin" over resources.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = 0
        # Small deterministic bias to keep movement stable.
        val -= 0.02 * (abs(dx) + abs(dy))
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_self == 0:
                # Collect if we're on it; dominate.
                val += 1000
                continue
            # Reach-before-opponent wins. Reward proportional to advantage.
            # If opponent is closer, still allow chasing but with penalty.
            margin = d_opp - d_self
            if margin > 0:
                val += 40 * margin - 0.5 * d_self
            elif margin == 0:
                val += 3 - 0.2 * d_self
            else:
                val -= 12 * (-margin) + 0.1 * d_self
        # Tie-break: prefer states that are closer to opponent-competitive resources, then lexicographic move.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]