def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    me = (sx, sy)
    opp = (ox, oy)

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    # Choose a resource where we can beat the opponent's reach (interception/opportunity maximization).
    best = None
    for r in resources:
        md = man(me, r)
        od = man(opp, r)
        # Prefer we are strictly closer; if tied, prefer closer overall; break ties deterministically.
        key = (-(od - md), md, r[0], r[1])
        if best is None or key < best[0]:
            best = (key, r)
    target = best[1]

    # Greedy step to reduce distance to chosen target, while avoiding obstacles and discouraging contact with opponent.
    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = man((nx, ny), target)
        # Small penalty if moving into opponent's immediate vicinity.
        opp_contact = 1 if man((nx, ny), opp) <= 1 else 0
        # Prefer diagonal only when it helps (tie-break).
        diag = 1 if dx != 0 and dy != 0 else 0
        key = (nd + 0.6 * opp_contact - 0.05 * diag, abs(dx) + abs(dy), dx, dy)
        if key < best_move:
            best_move = key
    if best_move[1] == 0 and best_move[2] == 0 and best_move[3] == 0:
        return [0, 0]
    return [int(best_move[2]), int(best_move[3])]