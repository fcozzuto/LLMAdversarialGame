def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role) or ("hunter" in role) or (not evader)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    fx, fy = far_corner

    def obstacle_proximity_pen(nx, ny):
        if not blocked:
            return 0
        best = 10**9
        for x, y in blocked:
            dd = (nx - x) * (nx - x) + (ny - y) * (ny - y)
            if dd < best:
                best = dd
        # Strongly discourage stepping adjacent to obstacles.
        if best == 0:
            return 10**6
        return 40 // (best + 1)

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)
        prox = obstacle_proximity_pen(nx, ny)

        # Small deterministic bias to break ties: prefer moving that changes x, then y.
        bias = 0
        if dx != 0:
            bias += 1 if dx > 0 else 0
        if dy != 0:
            bias += 1 if dy > 0 else 0

        if pursuer:
            # Pursuer: minimize distance; also bias toward cutting off by moving to the side of the opponent's relative position.
            relx, rely = nx - ox, ny - oy
            side = (relx * (sx - ox) + rely * (sy - oy))  # positive means "behind" relative to our position
            score = d + 0.7 * man + prox + (-0.15 * side) - 0.01 * bias
            better = (best_score is None) or (score < best_score)
        else:
            # Evader: maximize distance; also head toward farthest corner away from opponent.
            corner_pull = dist2(nx, ny, fx, fy)
            score = -d + 0.15 * corner_pull + prox + (-0.05 * bias)
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]